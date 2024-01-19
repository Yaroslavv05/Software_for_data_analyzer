import requests
from datetime import datetime, timedelta
import pytz
import openpyxl
import os

def calculation(high, low):
    result = ((high - low) / low) * 100
    return result


def format_timestamp(timestamp):
    dt = datetime.fromtimestamp(timestamp / 1000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def check_crossing(date, symbol, timeframe):
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
    url = f'https://api.twelvedata.com/time_series?apikey=7e1f42d9a4f743749ffa9e77958e06a4&interval=1min&symbol={symbol}&timezone=exchange&start_date={start_date}&end_date={end_date_datetime}'
    response = requests.get(url).json()['values'][::-1]
    
    previous = None
    active_flag = False
    
    for i in response:
        if active_flag:
            # Case 2: Check for H or L after crossing the middle of the active candle
            avg = (float(i['high']) + float(i['low'])) / 2
            # print("Timestamp:", format_timestamp(i['t']))
            # Check if the opening price crosses the average
            if float(i['open']) > avg:
                if float(i['high']) > previous_avg:
                    return '1'
                elif float(i['low']) < previous_avg:
                    return '0'
            # else:
            #     if float(i['low']) < previous_avg:
            #         return '0'
            #     else:
            #         return '1'
                
            active_flag = False  # Reset the active flag after processing
            
        # Case 1: Check for H or L before crossing the middle of the candle
        if float(i['high']) > float(i['low']):
            previous_avg = (float(i['high']) + float(i['low'])) / 2
            active_flag = True  # Set the active flag if H > L
            
        print(i)
    
url = 'https://api.twelvedata.com/time_series?apikey=7e1f42d9a4f743749ffa9e77958e06a4&interval=1h&symbol=AAPL&timezone=exchange&start_date=2024-01-02 00:00:00&end_date=2024-01-16 00:00:00&format=JSON'
response = requests.get(url=url).json()['values'][::-1]

interval_start = 1
interval_end = 2

output_data = []
for index, candle in enumerate(response):
    calculate = calculation(high=float(candle['high']), low=float(candle['low']))
    if interval_start <= calculate <= interval_end:
        print('ACTIVE')
        status = 'ACTIVE'
        # print("Timestamp:", format_timestamp(candle['datetime']))
        print(candle)
        # dt = datetime.fromtimestamp(candle['t'] / 1000)
        output = check_crossing(date=candle['datetime'], symbol='AAPL', timeframe='1h')
        print(output)
    else:
        status = 'NOT ACTIVE'
        # print("Timestamp:", format_timestamp(candle['datetime']))
        print('NOT ACTIVE')
        output = 2
        print(candle)
        print('2')
    # unix_timestamp_seconds = candle['datetime'] / 1000
    # unix_datetime = datetime.fromtimestamp(unix_timestamp_seconds, pytz.utc)
    # ny_timezone = pytz.timezone('America/New_York')
    # ny_datetime = unix_datetime.astimezone(ny_timezone)
    output_data.append({
        'time': candle['datetime'],
        'status': status,
        'output': output,
        'open': candle['open'],
        'close': candle['close'],
        'high': candle['high'],
        'low': candle['low'],
        # 'trade': candle['n'],
        'volume': candle['volume']
        
    })


wb = openpyxl.Workbook()
ws = wb.active

headers = ['Date', 'Status', 'Output', 'Open', 'Close', 'High', 'Low', 'Volume']
for col_index, header in enumerate(headers, 1):
    ws.cell(row=1, column=col_index, value=header)

for item in output_data:
    row_data = [item['time'], item['status'], item['output'], item['open'], item['close'], item['high'], item['low'], item['volume']]
    ws.append(row_data)
file_path = 'test.xlsx'
with open(file_path, 'wb') as file:
    wb.save(file)


# def analyze_candlestick(data, Alow, Aup):
#     result = []

#     for i in range(1, len(data)):
#         current_candle = data[i]
#         active_candle = data[i - 1]

#         # Check if the necessary keys exist in the current and active candles
#         if 'O' not in current_candle or 'H' not in current_candle or 'L' not in current_candle:
#             continue
#         if 'O' not in active_candle or 'H' not in active_candle or 'L' not in active_candle:
#             continue

#         # Calculate amplitude (A) of the given candlestick
#         A = ((current_candle['H'] - current_candle['L']) * 100) / current_candle['O']

#         if Alow <= A <= Aup:  # Candlestick is 'active'
#             # Calculate average value
#             Avg = (active_candle['H'] + active_candle['L']) / 2

#             # Divide the time interval into smaller intervals (e.g., 1 minute intervals)
#             time_intervals = 60  # 1 minute intervals
#             for j in range(time_intervals):
#                 # Calculate the opening price of the current interval
#                 current_open = current_candle['O'] + (current_candle['H'] - current_candle['O']) * j / time_intervals

#                 if current_open > Avg:  # Opening price crosses the Avg of the active candle
#                     if current_candle['H'] > Avg:  # Check if H crosses Avg or H of the active candle
#                         result.append((current_candle['timestamp'], 1))
#                     elif current_candle['L'] > Avg:  # Check if L crosses Avg or H of the active candle
#                         result.append((current_candle['timestamp'], 0))
#                 elif current_open < Avg:  # Opening price crosses the Avg of the active candle
#                     if current_candle['H'] < Avg:  # Check if H crosses Avg or L of the active candle
#                         result.append((current_candle['timestamp'], 0))
#                     elif current_candle['L'] < Avg:  # Check if L crosses Avg or L of the active candle
#                         result.append((current_candle['timestamp'], 1))

#     return result

# # Example usage:
# data = [
#     {'timestamp': '2022-01-01 00:00:00', 'O': 100, 'H': 120, 'L': 90},
#     {'timestamp': '2022-01-01 01:00:00', 'O': 110, 'H': 130, 'L': 95},
#     # Add more data as needed
# ]

# result = analyze_candlestick(data, Alow=1, Aup=5)
# print(result)

