import requests
from datetime import datetime, timedelta
import pytz
import openpyxl
import io

symbol = 'EURUSD'
timeframe = '1 day'
interval_start = 0.25
interval_end = 5
start_date = '2024-02-01'
end_date = '2024-02-10'
api_key = 'EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
interval_parts = timeframe.split()
  


def check_crossing_low(avg, previous_high, previous_low, date, symbol, timeframe):
    crossed_avg = False
    interval_mapping = {
        '1 minute': 0.0166666667,
        '5 minute': 0.0833333333,
        '15 minute': 0.25,
        '30 minute': 0.5,
        '45 minute': 0.75,
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
    print(start_date)
    start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    if start_date_datetime.time() == datetime.strptime("00:00:00", "%H:%M:%S").time():
        start_date_datetime = start_date_datetime.replace(hour=9, minute=30, second=0)
    else:
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    ny_timezone = pytz.timezone('America/New_York')
    start_date_datetime = ny_timezone.localize(start_date_datetime)
    end_date_datetime = start_date_datetime + timedelta(hours=interval_mapping[timeframe])
    start_unix_timestamp_milliseconds = int(start_date_datetime.timestamp()) * 1000
    end_unix_timestamp_milliseconds = int(end_date_datetime.timestamp()) * 1000
    url = f'https://api.polygon.io/v2/aggs/start_date_datetime/C:{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'

    response = requests.get(url).json()['results']
    print(avg, previous_high, previous_low, start_unix_timestamp_milliseconds, end_unix_timestamp_milliseconds, symbol, timeframe)

    for i, candle in enumerate(response):
        print(candle)
        if crossed_avg == False and candle['o'] < avg and candle['h'] > avg:
            crossed_avg = True
            print('Было пересечение средины')
        elif crossed_avg == False and candle['o'] > avg and candle['l'] < avg:
            crossed_avg = True
            print('Было пересечение средины')
        elif crossed_avg == False and candle['l'] < previous_low:
            output = '2'
            status = 'NOT ACTIVE'
            crossed_avg = False
            return output, status, crossed_avg 
        elif crossed_avg and candle['l'] < previous_low:
            output = '0'
            status = 'ACTIVE'
            crossed_avg = False
            return output, status, crossed_avg 
 
    return '1/0', 'ACTIVE', crossed_avg


def check_crossing_low_or_high(avg, previous_high, previous_low, date, symbol, timeframe):
    interval_mapping = {
        '1 minute': 0.0166666667,
        '5 minute': 0.0833333333,
        '15 minute': 0.25,
        '30 minute': 0.5,
        '45 minute': 0.75,
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
    print(start_date)
    start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    if start_date_datetime.time() == datetime.strptime("00:00:00", "%H:%M:%S").time():
        start_date_datetime = start_date_datetime.replace(hour=9, minute=30, second=0)
    else:
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    ny_timezone = pytz.timezone('America/New_York')
    start_date_datetime = ny_timezone.localize(start_date_datetime)
    end_date_datetime = start_date_datetime + timedelta(hours=interval_mapping[timeframe])
    start_unix_timestamp_milliseconds = int(start_date_datetime.timestamp()) * 1000
    end_unix_timestamp_milliseconds = int(end_date_datetime.timestamp()) * 1000
    url = f'https://api.polygon.io/v2/aggs/ticker/C:{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
    
    response = requests.get(url).json()['results']
    print(avg, previous_high, previous_low, start_unix_timestamp_milliseconds, end_unix_timestamp_milliseconds, symbol, timeframe)
    crossed_avg = False

    for i, candle in enumerate(response):
        print(candle)
        if crossed_avg == False and candle['o'] < avg and candle['h'] > avg:
            crossed_avg = True
            print('Было пересечение средины')
        elif crossed_avg == False and candle['o'] > avg and candle['l'] < avg:
            crossed_avg = True
            print('Было пересечение средины')
        elif crossed_avg == False and candle['l'] < previous_low:
            output = '2'
            status = 'NOT ACTIVE'
            return output, status 
        elif crossed_avg == False and candle['h'] > previous_high:
            output = '2'
            status = 'NOT ACTIVE'
            return output, status 
        elif crossed_avg and candle['h'] > previous_high:
            output = '1'
            status = 'ACTIVE'
            return output, status 
        elif crossed_avg and candle['l'] < previous_low:
            output = '0'
            status = 'ACTIVE'
            return output, status  


def check_crossing_high(avg, previous_high, previous_low, date, symbol, timeframe):
    crossed_avg = False
    interval_mapping = {
        '1 minute': 0.0166666667,
        '5 minute': 0.0833333333,
        '15 minute': 0.25,
        '30 minute': 0.5,
        '45 minute': 0.75,
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
    print(start_date)
    start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    if start_date_datetime.time() == datetime.strptime("00:00:00", "%H:%M:%S").time():
        start_date_datetime = start_date_datetime.replace(hour=9, minute=30, second=0)
    else:
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    ny_timezone = pytz.timezone('America/New_York')
    start_date_datetime = ny_timezone.localize(start_date_datetime)
    end_date_datetime = start_date_datetime + timedelta(hours=interval_mapping[timeframe])
    start_unix_timestamp_milliseconds = int(start_date_datetime.timestamp()) * 1000
    end_unix_timestamp_milliseconds = int(end_date_datetime.timestamp()) * 1000
    url = f'https://api.polygon.io/v2/aggs/ticker/C:{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
    

    response = requests.get(url).json()['results']
    print(avg, previous_high, previous_low, start_unix_timestamp_milliseconds, end_unix_timestamp_milliseconds, symbol, timeframe)

    for i, candle in enumerate(response):
        print(candle)
        if crossed_avg == False and candle['o'] > avg and candle['l'] < avg:
            crossed_avg = True
            print('Было пересечение средины')
        elif crossed_avg == False and candle['o'] > avg and candle['l'] < avg:
            crossed_avg = True
            print('Было пересечение средины')
        elif crossed_avg == False and candle['h'] > previous_high:
            output = '2'
            status = 'NOT ACTIVE'
            return output, status, crossed_avg
        elif crossed_avg and candle['h'] > previous_high:
            output = '1'
            status = 'ACTIVE'
            crossed_avg = False
            return output, status, crossed_avg
        
    return '1/0', 'ACTIVE', crossed_avg


url = f'https://api.polygon.io/v2/aggs/ticker/C:{symbol}/range/{interval_parts[0]}/{interval_parts[1]}/{start_date}/{end_date}?adjusted=true&sort=asc&limit=50000&apiKey={api_key}'

response = requests.get(url).json()['results']

avg = 0.0
previous_high = 0.0
previous_low = 0.0

output_data = []
for i in range(len(response) - 1):
    previous_candle = response[i - 1]
    candle = response[i]
    next_candle = response[i + 1]
    
    unix_timestamp_seconds = candle['t'] / 1000
    unix_datetime = datetime.fromtimestamp(unix_timestamp_seconds, pytz.utc)
    ny_timezone = pytz.timezone('America/New_York')
    ny_datetime = unix_datetime.astimezone(ny_timezone)
    time = ny_datetime.strftime("%Y-%m-%d %H:%M:%S")
    open_price = candle['o']
    high = candle['h']
    low = candle['l']
    close = candle['c'] 
    volume = candle['v']
    trade = candle['n']
    next_open = next_candle['o']
    amplitude = ((high - low) / low) * 100
    print(candle)
    unix_timestamp_seconds = next_candle['t'] / 1000
    unix_datetime = datetime.fromtimestamp(unix_timestamp_seconds, pytz.utc)
    ny_timezone = pytz.timezone('America/New_York')
    ny_datetime_next = unix_datetime.astimezone(ny_timezone)
    next_time = ny_datetime_next.strftime("%Y-%m-%d %H:%M:%S")
    if interval_start <= amplitude <= interval_end:
        avg = (high + low) / 2
        next_high = next_candle['h']
        next_low = next_candle['l']
        if high < next_high and next_low > avg:
            print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
            status = 'NOT ACTIVE'
            output = '2'
            print(status, output)
        elif next_open > avg and next_low < low and next_high < high:
            print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
            status = 'ACTIVE'
            output = '0'
            print(status, output)
        elif next_open < avg and next_high > high and next_low > low:
            print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
            status = 'ACTIVE'
            output = '1'
            print(status, output)
        elif next_high > high and next_low < low:
            print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
            output, status  = check_crossing_low_or_high(avg, high, low, next_time, symbol, timeframe)
            print(status, output)
        elif next_high > avg and next_low < avg and next_high < high and next_low > low:
            print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
            previous_high = high
            previous_low = low
            for j in response[i:-1]:
                if j['h'] > previous_high:
                    status = 'ACTIVE'
                    output = '1'
                    print(status, output)
                    break
                elif j['l'] < previous_low:
                    status = 'ACTIVE'
                    output = '0'
                    print(status, output)
                    break
        elif low > next_low and next_high < avg:
            print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
            status = 'NOT ACTIVE'
            output = '2'
            print(status, output)
        elif high < next_high and next_low < avg:
            print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
            output, status, crossed_avg  = check_crossing_high(avg, high, low, next_time, symbol, timeframe)
            print(status, output)
            if output == '1/0' and status == 'ACTIVE' and crossed_avg == True:
                previous_high = high
                previous_low = low
                for j in response[i:-1]:
                    if j['h'] > previous_high:
                        status = 'ACTIVE'
                        output = '1'
                        print(status, output)
                        break
                    elif j['l'] < previous_low:
                        status = 'ACTIVE'
                        output = '0'
                        print(status, output)
                        break
        elif low > next_low and next_high > avg:
            print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
            output, status, crossed_avg = check_crossing_low(avg, high, low, next_time, symbol, timeframe)
            print(status, output)
            if output == '1/0' and status == 'ACTIVE' and crossed_avg == True:
                previous_high = high
                previous_low = low
                for j in response[i:-1]:
                    if j['h'] > previous_high:
                        status = 'ACTIVE'
                        output = '1'
                        print(status, output)
                        break
                    elif j['l'] < previous_low:
                        status = 'ACTIVE'
                        output = '0'
                        print(status, output)
                        break
        else:
            status = 'NOT ACTIVE'
            output = '2'
            print(status, output)
    else:
        status = 'NOT ACTIVE'
        output = '2'
        print(status, output)
        
    output_data.append({
        'time': ny_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        'status': status,
        'output': output,
        'open': candle['o'],
        'close': candle['c'],
        'high': candle['h'],
        'low': candle['l'],
        'trade': candle['n'],
        'volume': candle['v']
    })
    
print(output_data)    
wb = openpyxl.Workbook()
ws = wb.active
headers = ['Date', 'Status', 'Output', 'Open', 'Close', 'High', 'Low', 'Trade', 'Volume']
for col_index, header in enumerate(headers, 1):
    ws.cell(row=1, column=col_index, value=header)

for item in output_data:
    row_data = [item['time'], item['status'], item['output'], item['open'], item['close'], item['high'], item['low'], item['trade'], item['volume']]
    ws.append(row_data)

output_buffer = io.BytesIO()
wb.save(output_buffer)
output_buffer.seek(0)

file_path = f'{symbol}_{timeframe}_{interval_start}%_{interval_end}%{start_date}_{end_date}(Polugon).xlsx'
file_path = file_path.replace(':', '_').replace('?', '_').replace(' ', '_')
with open(file_path, 'wb') as file:
    file.write(output_buffer.read())