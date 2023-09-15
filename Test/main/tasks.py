import io
from django.contrib.auth.models import User
from celery import shared_task
import yfinance as yf
import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta, timezone
import openpyxl
import time
import requests
import os
import re
from .models import DataEntry
from plyer import notification


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
    file_path = f"{symbol} data crypto(binance).xlsx"
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
    if len(date) == 10:
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    else:
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
            try:
                date_time = datetime.strptime(item['time'], '%Y-%m-%d %H:%M:%S')
                has_time = True
            except ValueError:
                has_time = False
            if has_time:
                ws.cell(row=day_count, column=1, value=datetime.strptime(item['time'], "%Y-%m-%d %H:%M:%S").date())
            else:
                ws.cell(row=day_count, column=1, value=datetime.strptime(item['time'], "%Y-%m-%d").date())
            ws.cell(row=day_count, column=col_index + 1, value=item['output'])
        day_count += 1
    output_buffer = io.BytesIO()
    wb.save(output_buffer)
    output_buffer.seek(0)
    file_path = f"{symbol} data shares(twelvedata).xlsx"
    with open(file_path, 'wb') as file:
        file.write(output_buffer.read())
    return file_path


def minute_shares_polygon(symbol, timeframe, open_price, date, bound):
    time.sleep(30)
    interval_mapping = {
        '1 minute': 0.0166666667,
        '5 minute': 0.05,
        '15 minute': 0.0833333333,
        '30 minute': 0.25,
        '45 minute': 0.375,
        '1 hour': 1.0,
        '2 hour': 2.0,
        '3 hour': 3.0,
        '4 hour': 4.0,
        '5 hour': 5.0,
        '6 hour': 6.0,
        '7 hour': 7.0,
        '8 hour': 8.0,
        '9 hour': 9.0,
        '10 hour': 10.0,
        '11 hour': 11.0,
        '12 hour': 12.0,
        '1 day': 24.0,
        '1 week': 168.0,
        '1 month': 720.0,
        '1 year': 8760
    }
    start_date = date
    start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date_datetime = start_date_datetime + timedelta(hours=interval_mapping[timeframe])
    start_unix_timestamp = int(start_date_datetime.timestamp())
    end_unix_timestamp = int(end_date_datetime.timestamp())
    start_unix_timestamp_milliseconds = start_unix_timestamp * 1000
    end_unix_timestamp_milliseconds = end_unix_timestamp * 1000
    response = requests.get(
        f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz")
    print(response.json())
    d = response.json()['results']
    mass = []
    for i in d:
        dt = datetime.fromtimestamp(i['t'] / 1000) - timedelta(hours=2)
        mass.append({
            'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'open': i['o'],
            'close': i['c'],
            'high': i['h'],
            'low': i['l']
        })

    for i in mass:
        if float(i['high']) - open_price >= bound:
            return '1'
        elif open_price - float(i['low']) >= bound:
            return '0'


@shared_task
def shares_polygon_async_task(data):
    symbol = data['symbol'].upper()
    timeframe = data['interval']
    bound = float(data['bound'])
    bound_unit = data['bound_unit']
    start_date = data['start_data']
    end_date = data['end_data']
    api = data['api']

    response = requests.get(
        f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{timeframe.split()[0]}/{timeframe.split()[1]}/{start_date}/{end_date}?adjusted=true&sort=asc&limit=50000&apiKey={api}')
    result = response.json()['results']
    mass = []
    for i in result:
        dt = datetime.fromtimestamp(i['t'] / 1000)
        mass.append({
            'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'open': i['o'],
            'close': i['c'],
            'high': i['h'],
            'low': i['l']
        })
    output_data = []
    if bound_unit == '$':
        for i in mass:
            if float(i['high']) - float(i['open']) >= bound and float(i['open']) - float(i['low']) >= bound:
                time = i['time']
                print(time)
                output = minute_shares_polygon(symbol=symbol, timeframe=timeframe, open_price=float(i['open']),
                                               date=i['time'], bound=bound)
            elif float(i['high']) - float(i['open']) >= bound:
                time = i['time']
                output = '1'
            elif float(i['open']) - float(i['low']) >= bound:
                time = i['time']
                output = '0'
            else:
                time = i['time']
                output = '2'
            output_data.append({'time': time, 'output': output})
    elif bound_unit == '%':
        for i in mass:
            if float(i['high']) - float(i['open']) >= (float(i['open']) / 100 * bound) and float(i['open']) - float(
                    i['low']) >= (float(i['open']) / 100 * bound):
                time = i['time']
                output = minute_shares_polygon(symbol=symbol, timeframe=timeframe, open_price=float(i['open']),
                                               date=i['time'], bound=(float(i['open']) / 100 * bound))
            elif float(i['high']) - float(i['open']) >= (float(i['open']) / 100 * bound):
                time = i['time']
                output = '1'
            elif float(i['open']) - float(i['low']) >= (float(i['open']) / 100 * bound):
                time = i['time']
                output = '0'
            else:
                time = i['time']
                output = '2'
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
    file_path = f"{symbol} data shares(polygon).xlsx"
    with open(file_path, 'wb') as file:
        file.write(output_buffer.read())
    return file_path


def send_notification_at_time(datetime_str):
    current_time = datetime.now()

    try:
        target_time = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
    except ValueError:
        print("Неверный формат даты и времени. Используйте формат 'ГГГГ-ММ-ДД ЧЧ:ММ'")
        return False

    if target_time <= current_time:
        print('Время пришло')
        return True

    time_until_notification = target_time - current_time
    delay = time_until_notification.total_seconds()

    if delay > 0:
        print(f"Уведомление будет отправлено через {time_until_notification}")
        time.sleep(delay)
        notification.notify(
            title='Уведомление',
            message='Пора!',
            app_name='ВашеПриложение'
        )
        return True
    else:
        print("Указанное время уже прошло.")
        return False


def trade(symbol, api_key, secret_key, leverage, amount_usdt, position):
    client = Client(api_key, secret_key, testnet=True)

    price = client.futures_mark_price(symbol=symbol)['markPrice']
    change_leverage = client.futures_change_leverage(symbol=symbol, leverage=leverage)

    col_vo_usdt = round((float(amount_usdt) * int(leverage)) / float(price), 3)
    print(col_vo_usdt, change_leverage)
    if position == '1':
        limit_order_long = client.futures_create_order(
            symbol=symbol,
            side='BUY',
            positionSide='LONG',
            type='LIMIT',
            quantity=col_vo_usdt,
            timeInForce='GTC',
            price=round(float(price), 0))
        print(limit_order_long)
    elif position == '0':
        limit_order_short = client.futures_create_order(
            symbol=symbol,
            side='SELL',
            positionSide='SHORT',
            type='LIMIT',
            quantity=col_vo_usdt,
            timeInForce='GTC',
            price=round(float(price), 0))
        print(limit_order_short)
    else:
        print('Получин не опознаный символ')


@shared_task
def async_parse_file_task(file_path, user_id, symbol, amount_usdt, leverage, api_key, secret_key):
    workbook = openpyxl.load_workbook(f'media/{file_path}')
    sheet = workbook['Sheet']
    data = []
    user = User.objects.get(pk=user_id)

    for row in sheet.iter_rows(values_only=True):
        data.append(row)

    current_time = datetime.strptime('00:00', '%H:%M')

    for row in data:
        if len(row) == 1441:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol, amount_usdt=amount_usdt, leverage=leverage, api_key=api_key, secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=0.0166666667)
        elif len(row) == 481:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol, amount_usdt=amount_usdt, leverage=leverage, api_key=api_key, secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=0.05)
        elif len(row) == 289:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol, amount_usdt=amount_usdt, leverage=leverage, api_key=api_key, secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=0.0833333333)
        elif len(row) == 97:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol, amount_usdt=amount_usdt, leverage=leverage, api_key=api_key, secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=0.25)
        elif len(row) == 49:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol, amount_usdt=amount_usdt, leverage=leverage, api_key=api_key, secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=0.5)
        elif len(row) == 25:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol, amount_usdt=amount_usdt, leverage=leverage, api_key=api_key, secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=1)
        elif len(row) == 13:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol, amount_usdt=amount_usdt, leverage=leverage, api_key=api_key, secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=2)
        elif len(row) == 7:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol, amount_usdt=amount_usdt, leverage=leverage, api_key=api_key, secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=4)
        elif len(row) == 5:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol,
                                       amount_usdt=amount_usdt, leverage=leverage, api_key=api_key,
                                       secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=6)
        elif len(row) == 4:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol,
                                       amount_usdt=amount_usdt, leverage=leverage, api_key=api_key,
                                       secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=8)
        elif len(row) == 3:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol,
                                       amount_usdt=amount_usdt, leverage=leverage, api_key=api_key,
                                       secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=12)
        elif len(row) == 2:
            date = row[0]
            for i in row[1:]:
                combined_datetime = datetime.combine(date, current_time.time())
                position = i

                formatted_datetime = combined_datetime.strftime('%Y-%m-%d %H:%M')
                data_entry = DataEntry(user=user, date=formatted_datetime, position=position, symbol=symbol,
                                       amount_usdt=amount_usdt, leverage=leverage, api_key=api_key,
                                       secret_key=secret_key)
                data_entry.save()

                current_time += timedelta(hours=24)
        else:
            break
    current_datetime = datetime.now()
    entries_to_process = DataEntry.objects.filter(user=user_id, is_completed=False)
    for entry in entries_to_process:
        print(entry.date, entry.position, entry.symbol, entry.amount_usdt, entry.leverage, entry.api_key, entry.secret_key)
        entry_datetime = datetime.strptime(entry.date, '%Y-%m-%d %H:%M')
        if entry_datetime > current_datetime:
            if send_notification_at_time(f"{entry_datetime.strftime('%Y-%m-%d %H:%M')}"):
                print('yes')
                trade(symbol=entry.symbol, api_key=entry.api_key, secret_key=entry.secret_key, leverage=entry.leverage, amount_usdt=entry.amount_usdt, position=entry.position)
                entry.is_completed = True
                entry.save()


def minute_shares_yfinance(symbol, timeframe, open_price, date, bound):
    interval_mapping = {
        '1m': 0.0166666667,
        '2m': 0.0333333333333333,
        '5m': 0.05,
        '15m': 0.0833333333,
        '30m': 0.25,
        '90m': 1.5,
        '1h': 1.0,
        '1d': 24.0,
        '5d': 120.0,
        '1wk': 168.0,
        '1mo': 720.0,
        '3mo': 2160.0
    }
    start_date = date
    if len(date) == 10:
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date_datetime = start_date_datetime + timedelta(hours=interval_mapping[timeframe])
    data = yf.download(symbol, start=start_date_datetime, end=end_date_datetime, interval='1m')

    csv_filename = "historical_data_1m.csv"

    data.to_csv(csv_filename)

    data = pd.read_csv(csv_filename)
    data_dict = data.to_dict(orient="records")

    if os.path.exists(csv_filename):
        os.remove(csv_filename)
        print(f"Файл {csv_filename} удален.")

    for i in data_dict:
        if float(i['High']) - open_price >= bound:
            return '1'
        elif open_price - float(i['Low']) >= bound:
            return '0'


@shared_task
def shares_yfinance_async_task(data):
    symbol = data['symbol'].upper()
    start_date = data['start_data']
    end_date = data['end_data']
    end_date_inclusive = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    timeframe = data['interval']
    bound = float(data['bound'])
    bound_unit = data['bound_unit']

    data = yf.download(symbol, start=start_date, end=end_date_inclusive, interval=timeframe)

    csv_filename = "historical_data.csv"

    data.to_csv(csv_filename)

    data = pd.read_csv(csv_filename)
    if timeframe == '1d' or timeframe == '5d' or timeframe == '1wk' or timeframe == '1mo' or timeframe == '3mo':
        name = 'Date'
    else:
        data["Datetime"] = data["Datetime"].str.replace("-04:00", "")
        name = 'Datetime'
    data_dict = data.to_dict(orient="records")

    if os.path.exists(csv_filename):
        os.remove(csv_filename)
        print(f"Файл {csv_filename} удален.")

    output_data = []
    if bound_unit == '$':
        for i in data_dict:
            if float(i['High']) - float(i['Open']) >= bound and float(i['Open']) - float(i['Low']) >= bound:
                time = i[name]
                output = minute_shares_yfinance(symbol=symbol, timeframe=timeframe, open_price=float(i['Open']),
                                                date=time,
                                                bound=bound)
            elif float(i['High']) - float(i['Open']) >= bound:
                time = i[name]
                output = '1'
            elif float(i['Open']) - float(i['Low']) >= bound:
                time = i[name]
                output = '0'
            else:
                time = i[name]
                output = '2'
            output_data.append({'time': time, 'output': output})
    elif bound_unit == '%':
        for i in data_dict:
            if float(i['High']) - float(i['Open']) >= (float(i['Open']) / 100 * bound) and float(i['Open']) - float(
                    i['Low']) >= (float(i['Open']) / 100 * bound):
                time = i[name]
                output = minute_shares_yfinance(symbol=symbol, timeframe=timeframe, open_price=float(i['Open']),
                                                date=time,
                                                bound=bound)
            elif float(i['High']) - float(i['Open']) >= (float(i['Open']) / 100 * bound):
                time = i[name]
                output = '1'
            elif float(i['Open']) - float(i['Low']) >= (float(i['Open']) / 100 * bound):
                time = i[name]
                output = '0'
            else:
                time = i[name]
                output = '2'
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
            try:
                date_time = datetime.strptime(item['time'], '%Y-%m-%d %H:%M:%S')
                has_time = True
            except ValueError:
                has_time = False
            if has_time:
                ws.cell(row=day_count, column=1, value=datetime.strptime(item['time'], "%Y-%m-%d %H:%M:%S").date())
            else:
                ws.cell(row=day_count, column=1, value=datetime.strptime(item['time'], "%Y-%m-%d").date())
            ws.cell(row=day_count, column=col_index + 1, value=item['output'])
        day_count += 1

    output_buffer = io.BytesIO()
    wb.save(output_buffer)
    output_buffer.seek(0)
    file_path = f"{symbol} data shares(yfinance).xlsx"
    with open(file_path, 'wb') as file:
        file.write(output_buffer.read())
    return file_path