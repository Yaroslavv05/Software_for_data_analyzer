import requests
from datetime import datetime, timedelta
import pytz
import openpyxl
import io

symbol = 'AAPL'
timeframe = '1 day'
interval_start = 0
interval_end = 100
start_date = '2024-01-01'
end_date = '2024-01-28'
api_key = 'EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
interval_parts = timeframe.split()
  


def check_crossing_low(avg, previous_high, previous_low, date, symbol, timeframe):
    try:
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
            start_date_datetime = start_date_datetime.replace(hour=4, minute=0, second=0)
        else:
            start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        ny_timezone = pytz.timezone('America/New_York')
        start_date_datetime = ny_timezone.localize(start_date_datetime)
        end_date_datetime = start_date_datetime + timedelta(hours=interval_mapping[timeframe])
        start_unix_timestamp_milliseconds = int(start_date_datetime.timestamp()) * 1000
        end_unix_timestamp_milliseconds = int(end_date_datetime.timestamp()) * 1000
        url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        
        response = requests.get(url).json()['results']
        print(avg, previous_high, previous_low, start_unix_timestamp_milliseconds, end_unix_timestamp_milliseconds, symbol, timeframe)
        crossed_avg = False

        for i, candle in enumerate(response):
            print(candle)
            if crossed_avg == False and candle['o'] < avg and candle['h'] > avg:
                crossed_avg = True
                print('Было пересечение средины')
            elif crossed_avg == False and candle['l'] < previous_low:
                output = '2'
                status = 'NOT ACTIVE'
                return output, status
            elif crossed_avg and candle['l'] < previous_low:
                output = '0'
                status = 'ACTIVE'
                return output, status
    except Exception as e:
        print(e)  


def check_crossing_high(avg, previous_high, previous_low, date, symbol, timeframe):
    try:
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
            start_date_datetime = start_date_datetime.replace(hour=4, minute=0, second=0)
        else:
            start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        ny_timezone = pytz.timezone('America/New_York')
        start_date_datetime = ny_timezone.localize(start_date_datetime)
        end_date_datetime = start_date_datetime + timedelta(hours=interval_mapping[timeframe])
        start_unix_timestamp_milliseconds = int(start_date_datetime.timestamp()) * 1000
        end_unix_timestamp_milliseconds = int(end_date_datetime.timestamp()) * 1000
        url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        
        response = requests.get(url).json()['results']
        print(avg, previous_high, previous_low, start_unix_timestamp_milliseconds, end_unix_timestamp_milliseconds, symbol, timeframe)
        crossed_avg = False

        for i, candle in enumerate(response):
            print(candle)
            if crossed_avg == False and candle['o'] > avg and candle['l'] < avg:
                crossed_avg = True
                print('Было пересечение средины')
            elif crossed_avg == False and candle['h'] > previous_high:
                output = '2'
                status = 'NOT ACTIVE'
                return output, status
            elif crossed_avg and candle['h'] > previous_high:
                output = '1'
                status = 'ACTIVE'
                return output, status                
    except Exception as e:
        print(e)


url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{interval_parts[0]}/{interval_parts[1]}/{start_date}/{end_date}?adjusted=true&sort=asc&limit=50000&apiKey={api_key}'

response = requests.get(url).json()['results']

first_active_found = False
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
    amplitude = ((high - low) / low) * 100
    print(candle)
    if interval_start <= amplitude <= interval_end and not first_active_found:
        avg = (high + low) / 2
        if next_candle['l'] < avg and next_candle['o'] > avg  or next_candle['h'] > avg and next_candle['o'] < avg:
            status = 'ACTIVE'
            output = '1'
            print(status, output)
            first_active_found = True
            avg = (high + low) / 2
            previous_high = high
            previous_low = low
        else:
            status = 'NOT ACTIVE'
            output = '2'
            print(status, output)
    else:
        if first_active_found == True:
            if previous_high < high and low > avg:
                print(f'previous_high - {previous_high}\nhigh - {high}\nlow - {low}\navg - {avg}\nprevious low - {previous_low}')
                status = 'NOT ACTIVE'
                output = '2'
                print(status, output)
            elif previous_low > low and high < avg:
                print(f'previous_high - {previous_high}\nhigh - {high}\nlow - {low}\navg - {avg}\nprevious low - {previous_low}')
                status = 'NOT ACTIVE'
                output = '2'
                print(status, output)
            elif previous_high < high and low < avg:
                print(f'previous_high - {previous_high}\nhigh - {high}\nlow - {low}\navg - {avg}\nprevious low - {previous_low}')
                try:
                    output, status  = check_crossing_high(avg, previous_high, previous_low, time, symbol, timeframe)
                except:
                    status = 'NOT ACTIVE'
                    output = '2'
                print(status, output)
                if status == 'ACTIVE':
                    avg = (high + low) / 2
                    previous_high = high
                    previous_low = low
            elif previous_low > low and high > avg:
                print(f'previous_high - {previous_high}\nhigh - {high}\nlow - {low}\navg - {avg}\nprevious low - {previous_low}')
                try:
                    output, status = check_crossing_low(avg, previous_high, previous_low, time, symbol, timeframe)
                except:
                    status = 'NOT ACTIVE'
                    output = '2'
                print(status, output)
                if status == 'ACTIVE':
                    avg = (high + low) / 2
                    previous_high = high
                    previous_low = low
            elif previous_candle['l'] > low and previous_high < high:
                print(f'previous_high - {previous_high}\nhigh - {high}\nlow - {low}\navg - {avg}\nprevious low - {previous_low}')
                status = 'NOT ACTIVE'   
                output = '1/0/2'
                print(status, output)
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