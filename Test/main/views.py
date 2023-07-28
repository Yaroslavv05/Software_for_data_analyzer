from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MyForm
from binance.client import Client
from datetime import datetime, timedelta
import openpyxl
from django.http import HttpResponse
import os
import re


def index(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            pattern = r'^[a-zA-Z]+$'
            if form.cleaned_data['end_data'] < form.cleaned_data['start_data']:
                messages.error(request, 'Дата окончания должна быть позже даты начала!')
            elif not re.match(pattern, form.cleaned_data['symbol']):
                messages.error(request, 'Недопустимый символ. Символ может содержать только буквы!')
            elif float(form.cleaned_data['bound']) < 0:
                messages.error(request, 'Bound не может быть отрицательным!')
            else:
                client = Client()
                symbol = form.cleaned_data['symbol'].upper()
                timeframe = float(form.cleaned_data['interval']) * 60
                bound = float(form.cleaned_data['bound'])
                bound_unit = form.cleaned_data['bound_unit']

                interval = Client.KLINE_INTERVAL_1MINUTE

                start_date_str = form.cleaned_data['start_data']
                if 'T' in start_date_str:
                    start_date = datetime.fromisoformat(start_date_str)
                else:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

                end_date_str = form.cleaned_data['end_data']
                if 'T' in end_date_str:
                    end_date = datetime.fromisoformat(end_date_str)
                else:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    end_date = end_date + timedelta(days=1)

                difference = end_date - start_date
                num_days = int(difference.days)
                minutes = num_days * 24 * 60
                hours = int(minutes / timeframe)

                start_timestamp = int(start_date.timestamp()) * 1000
                end_timestamp = int(end_date.timestamp()) * 1000

                klines = client.get_historical_klines(symbol, interval, start_timestamp, end_timestamp)

                mass = []

                for kline in klines:
                    time = datetime.fromtimestamp(kline[0] / 1000)
                    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    mass.append({
                        'time': formatted_time,
                        'open': kline[1],
                        'close': kline[4]
                    })
                output_data = []
                total = 0
                if bound_unit == '$':
                    for i in range(hours):
                        if i == 0:
                            if (float(mass[total]['open']) - float(mass[total]['close'])) * (-1) >= bound:
                                time = mass[total]['time']
                                output = '1'
                            elif float(mass[total]['open']) - float(mass[total]['close']) >= bound:
                                time = mass[total]['time']
                                output = '0'
                            else:
                                output = '2'
                                time = mass[total]['time']
                            print(mass[total])
                        else:
                            total += int(timeframe)
                            if (float(mass[total]['open']) - float(mass[total]['close'])) * (-1) >= bound:
                                output = '1'
                                time = mass[total]['time']
                            elif float(mass[total]['open']) - float(mass[total]['close']) >= bound:
                                output = '0'
                                time = mass[total]['time']
                            else:
                                output = '2'
                                time = mass[total]['time']
                            print(mass[total])

                        output_data.append({'time': time, 'output': output})
                elif bound_unit == '%':
                    for i in range(hours):
                        if i == 0:
                            if (float(mass[total]['open']) - float(mass[total]['close'])) * (-1) >= (float(mass[total]['open']) / 100 * bound):
                                output = '1'
                                time = mass[total]['time']
                            elif float(mass[total]['open']) - float(mass[total]['close']) >= (float(mass[total]['open']) / 100 * bound):
                                output = '0'
                                time = mass[total]['time']
                            else:
                                output = '2'
                                time = mass[total]['time']
                            print(mass[total])
                        else:
                            total += int(timeframe)
                            if (float(mass[total]['open']) - float(mass[total]['close'])) * (-1) >= (float(mass[total]['open']) / 100 * bound):
                                output = '1'
                                time = mass[total]['time']
                            elif float(mass[total]['open']) - float(mass[total]['close']) >= (float(mass[total]['open']) / 100 * bound):
                                output = '0'
                                time = mass[total]['time']
                            else:
                                output = '2'
                                time = mass[total]['time']
                            print(mass[total])

                        output_data.append({'time': time, 'output': output})
                wb = openpyxl.Workbook()
                ws = wb.active
                daily_data = {}
                day_count = 1
                for item in output_data:
                    day = item['time'][:10]
                    if day in daily_data:
                        daily_data[day].append(item)
                    else:
                        daily_data[day] = [item]

                for day_data in daily_data.values():
                    for col_index, item in enumerate(day_data, 1):
                        ws.cell(row=day_count, column=col_index, value=item['output'])
                    day_count += 1
                file_path = f"{symbol} data.xlsx"
                wb.save(file_path)
                request.session['file_name'] = file_path
                return redirect('result')
    else:
        form = MyForm()

    return render(request, 'index.html', {'form': form})


def result(request):
    file_name = request.session.get('file_name', None)
    if file_name and os.path.exists(file_name):
        with open(file_name, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
            return response
    else:
        return HttpResponse("File not found.")
