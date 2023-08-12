from django.shortcuts import render, redirect
from django.contrib import messages
from binance.client import Client
from .forms import MyForm
from django.http import HttpResponse
import os
from .tasks import process_data_async


def main(request):
    return render(request, 'main.html')


def get_binance_symbols():
    client = Client()
    exchange_info = client.get_exchange_info()
    symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
    return symbols


def index(request):
    form = MyForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            interval = form.cleaned_data['interval']
            bound = form.cleaned_data['bound']
            bound_unit = form.cleaned_data['bound_unit']
            start_data = form.cleaned_data['start_data']
            end_data = form.cleaned_data['end_data']
            data = {
                'symbol': symbol,
                'interval': interval,
                'bound': bound,
                'bound_unit': bound_unit,
                'start_data': start_data,
                'end_data': end_data
            }
            process_data_async.delay(data)
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
