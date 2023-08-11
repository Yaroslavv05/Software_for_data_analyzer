from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MyForm
from binance.client import Client
from datetime import datetime, timedelta
import openpyxl
from django.http import HttpResponse
from .models import MyData
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FormDataSerializer


class FormSubmissionView(APIView):
    def post(self, request, format=None):
        serializer = FormDataSerializer(data=request.data)
        if serializer.is_valid():
            # Получите данные из валидированного сериализатора
            field1_value = serializer.validated_data['field1']
            field2_value = serializer.validated_data['field2']

            # Здесь выполняется логика алгоритма над данными
            # ...

            # Генерация файла
            file_content = "Содержимое файла"
            file_name = "example.txt"

            # Создание HTTP-ответа с файлом
            response = Response(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def main(request):
    return render(request, 'main.html')


def minute(symbol, open_price, bound, date, time_frame):
    client = Client()
    interval = Client.KLINE_INTERVAL_1MINUTE
    start_date = date
    start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=2)
    end_date_datetime = start_date_datetime + timedelta(hours=time_frame)

    klines = client.futures_historical_klines(symbol, interval, start_date_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                                              end_date_datetime.strftime('%Y-%m-%d %H:%M:%S'))

    mass = []

    for kline in klines:
        time = datetime.fromtimestamp(kline[0] / 1000)
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
        mass.append({
            'time': formatted_time,
            'open': kline[1],
            'high': kline[2],
            'low': kline[3],
        })
    open_price = open_price
    bound = bound
    for i in mass:
        if (float(i['high']) - open_price) >= bound:
            return '1'
        elif open_price - float(i['low']) >= bound:
            return '0'


def get_binance_symbols():
    client = Client()
    exchange_info = client.get_exchange_info()
    symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
    return symbols


def index(request):
    form = MyForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            MyData.objects.create(
                symbol=form.cleaned_data['symbol'],
                interval=form.cleaned_data['interval'],
                bound=form.cleaned_data['bound'],
                bound_unit=form.cleaned_data['bound_unit'],
                start_data=form.cleaned_data['start_data'],
                end_data=form.cleaned_data['end_data']
            )
            return redirect('process')
    else:
        form = MyForm()
    return render(request, 'index.html', {'form': form})


def process(request):
    return render(request, 'proces.html')


def result(request):
    file_name = request.session.get('file_name', None)
    if file_name and os.path.exists(file_name):
        with open(file_name, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
            return response
    else:
        return HttpResponse("File not found.")
