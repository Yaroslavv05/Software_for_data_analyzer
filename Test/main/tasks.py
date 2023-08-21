import io
from celery import shared_task
from binance.client import Client
from datetime import datetime, timedelta
import openpyxl
import time
import requests
import re


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


@shared_task
def process_data_async(data):
    client = Client()
    symbol = data['symbol'].upper()
    timeframe = float(data['interval']) * 60
    bound = float(data['bound'])
    bound_unit = data['bound_unit']
    inter = data['interval']
    print(symbol, timeframe, bound, bound_unit, inter)
    interval_mapping = {
        0.0166666667: Client.KLINE_INTERVAL_1MINUTE,
        0.05: Client.KLINE_INTERVAL_3MINUTE,
        0.0833333333: Client.KLINE_INTERVAL_5MINUTE,
        0.25: Client.KLINE_INTERVAL_15MINUTE,
        0.5: Client.KLINE_INTERVAL_30MINUTE,
        1.0: Client.KLINE_INTERVAL_1HOUR,
        2.0: Client.KLINE_INTERVAL_2HOUR,
        4.0: Client.KLINE_INTERVAL_4HOUR,
        6.0: Client.KLINE_INTERVAL_6HOUR,
        8.0: Client.KLINE_INTERVAL_8HOUR,
        12.0: Client.KLINE_INTERVAL_12HOUR,
        24.0: Client.KLINE_INTERVAL_1DAY,
        72.0: Client.KLINE_INTERVAL_3DAY,
        168.0: Client.KLINE_INTERVAL_1WEEK,
        720.0: Client.KLINE_INTERVAL_1MONTH
    }

    start_date_str = data['start_data']
    if 'T' in start_date_str:
        start_date = datetime.fromisoformat(start_date_str)
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

    end_date_str = data['end_data']
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

    klines = client.futures_historical_klines(symbol, interval_mapping.get(float(inter), None), start_timestamp, end_timestamp)

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
    output_data = []
    total = 0
    if bound_unit == '$':
        for i in range(hours):
            if i == 0:
                if (float(mass[i]['high']) - float(mass[i]['open'])) >= bound and float(
                        mass[i]['open']) - float(mass[i]['low']) >= bound:
                    time = mass[i]['time']
                    output = minute(symbol=symbol, open_price=float(mass[i]['open']), bound=bound, date=time,
                                    time_frame=float(data['interval']))
                elif (float(mass[i]['high']) - float(mass[i]['open'])) >= bound:
                    time = mass[i]['time']
                    output = '1'
                elif float(mass[i]['open']) - float(mass[i]['low']) >= bound:
                    time = mass[i]['time']
                    output = '0'
                else:
                    output = '2'
                    time = mass[i]['time']
                print(mass[total])
            else:
                total += int(timeframe)
                if (float(mass[i]['high']) - float(mass[i]['open'])) >= bound and float(
                        mass[i]['open']) - float(mass[i]['low']) >= bound:
                    time = mass[i]['time']
                    output = minute(symbol=symbol, open_price=float(mass[i]['open']), bound=bound, date=time,
                                    time_frame=float(data['interval']))
                elif (float(mass[i]['high']) - float(mass[i]['open'])) >= bound:
                    time = mass[i]['time']
                    output = '1'
                elif float(mass[i]['open']) - float(mass[i]['low']) >= bound:
                    time = mass[i]['time']
                    output = '0'
                else:
                    output = '2'
                    time = mass[i]['time']
                print(mass[i])
            output_data.append({'time': time, 'output': output})
    elif bound_unit == '%':
        for i in range(hours):
            if i == 0:
                if (float(mass[i]['high']) - float(mass[i]['open'])) >= (
                        float(mass[total]['open']) / 100 * bound) and float(mass[i]['open']) - float(
                    mass[i]['low']) >= (float(mass[total]['open']) / 100 * bound):
                    time = mass[i]['time']
                    output = minute(symbol=symbol, open_price=float(mass[i]['open']),
                                    bound=(float(mass[i]['open']) / 100 * bound), date=time,
                                    time_frame=float(data['interval']))
                elif (float(mass[i]['high']) - float(mass[i]['open'])) >= (
                        float(mass[i]['open']) / 100 * bound):
                    output = '1'
                    time = mass[i]['time']
                elif float(mass[i]['open']) - float(mass[i]['low']) >= (float(mass[i]['open']) / 100 * bound):
                    output = '0'
                    time = mass[i]['time']
                else:
                    output = '2'
                    time = mass[i]['time']
                print(mass[total])
            else:
                total += int(timeframe)
                if (float(mass[i]['high']) - float(mass[i]['open'])) >= (
                        float(mass[i]['open']) / 100 * bound) and float(mass[i]['open']) - float(
                    mass[i]['low']) >= (float(mass[i]['open']) / 100 * bound):
                    time = mass[i]['time']
                    output = minute(symbol=symbol, open_price=float(mass[i]['open']),
                                    bound=(float(mass[i]['open']) / 100 * bound), date=time,
                                    time_frame=float(data['interval']))
                elif (float(mass[i]['high']) - float(mass[i]['open'])) >= (
                        float(mass[i]['open']) / 100 * bound):
                    output = '1'
                    time = mass[i]['time']
                elif float(mass[i]['open']) - float(mass[i]['low']) >= (float(mass[i]['open']) / 100 * bound):
                    output = '0'
                    time = mass[i]['time']
                else:
                    output = '2'
                    time = mass[i]['time']
                print(mass[i])

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
            ws.cell(row=day_count, column=1, value=datetime.strptime(item['time'], "%Y-%m-%d %H:%M:%S").date())
            ws.cell(row=day_count, column=col_index + 1, value=item['output'])
        day_count += 1

    output_buffer = io.BytesIO()
    wb.save(output_buffer)
    output_buffer.seek(0)
    file_path = f"{symbol} data crypto.xlsx"
    with open(file_path, 'wb') as file:
        file.write(output_buffer.read())

    return file_path


def controversial(symbol, timeframe, open_price, date, bound):
    interval_mapping = {
        '1min': 0.0166666667,
        '5min': 0.05,
        '15min': 0.0833333333,
        '30min': 0.25,
        '45min': 0.375,
        '1h': 1.0,
        '2h': 2.0,
        '4h': 4.0,
        '1day': 24.0,
        '1week': 168.0,
        '1month': 720.0
    }
    start_date = date
    start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date_datetime = start_date_datetime + timedelta(hours=float(interval_mapping[timeframe]))
    print(symbol, timeframe, bound, start_date, end_date_datetime)
    response = requests.get(f"https://api.twelvedata.com/time_series?apikey=7e1f42d9a4f743749ffa9e77958e06a4&interval=1min&symbol={symbol}&timezone=utc&start_date={start_date}&end_date={end_date_datetime}")
    d = response.json()['values']

    for j in d:
        if float(j['high']) - open_price >= bound:
            return '1'
        elif open_price - float(j['low']) >= bound:
            return '0'


@shared_task
def shared_async_task(data):
    symbol = data['symbol'].upper()
    timeframe = data['interval']
    bound = float(data['bound'])
    bound_unit = data['bound_unit']
    start_date_input = data['start_data']
    end_date_input = data['end_data']

    if len(start_date_input) == 10:
        start_date_input += ' 00:00:00'

    if len(end_date_input) == 10:
        end_date_input += ' 00:00:00'

    start_date = datetime.strptime(start_date_input, '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date_input, '%Y-%m-%d %H:%M:%S') + timedelta(days=1)

    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    print(symbol, timeframe, bound, bound_unit, start_date, end_date)
    response = requests.get(
        f"https://api.twelvedata.com/time_series?apikey=7e1f42d9a4f743749ffa9e77958e06a4&interval={timeframe}&symbol={symbol}&timezone=utc&start_date={start_date_str}&end_date={end_date_str}")

    data = response.json()['values']

    output_data = []
    if bound_unit == '$':
        for i in data:
            if float(i['high']) - float(i['open']) >= bound and float(i['open']) - float(i['low']) >= bound:
                times = i['datetime']
                output = controversial(symbol=symbol, timeframe=timeframe,
                                       open_price=float(i['open']), date=i['datetime'], bound=bound)
                time.sleep(10)
            elif float(i['high']) - float(i['open']) >= bound:
                times = i['datetime']
                output = '1'
            elif float(i['open']) - float(i['low']) >= bound:
                times = i['datetime']
                output = '0'
            else:
                times = i['datetime']
                output = '2'
            output_data.append({'time': times, 'output': output})
    elif bound_unit == '%':
        for i in data:
            if float(i['high']) - float(i['open']) >= (float(i['open']) / 100 * bound) and float(i['open']) - float(
                    i['low']) >= (float(i['open']) / 100 * bound):
                times = i['datetime']
                output = controversial(symbol=symbol, timeframe=timeframe,
                                       open_price=float(i['open']), date=i['datetime'],
                                       bound=(float(i['open']) / 100 * bound))
                time.sleep(10)
            elif float(i['high']) - float(i['open']) >= (float(i['open']) / 100 * bound):
                times = i['datetime']
                output = '1'
            elif float(i['open']) - float(i['low']) >= (float(i['open']) / 100 * bound):
                times = i['datetime']
                output = '0'
            else:
                times = i['datetime']
                output = '2'
            output_data.append({'time': times, 'output': output})
    wb = openpyxl.Workbook()
    ws = wb.active
    daily_data = {}
    day_count = 1
    for item in output_data[::-1]:
        day = item['time'][:10]
        if day in daily_data:
            daily_data[day].append(item)
        else:
            daily_data[day] = [item]

    for day_data in daily_data.values():
        for col_index, item in enumerate(day_data, 1):
            ws.cell(row=day_count, column=1, value=datetime.strptime(item['time'], "%Y-%m-%d %H:%M:%S").date())
            ws.cell(row=day_count, column=col_index + 1, value=item['output'])
        day_count += 1
    output_buffer = io.BytesIO()
    wb.save(output_buffer)
    output_buffer.seek(0)
    file_path = f"{symbol} data shares.xlsx"
    with open(file_path, 'wb') as file:
        file.write(output_buffer.read())

    return file_path