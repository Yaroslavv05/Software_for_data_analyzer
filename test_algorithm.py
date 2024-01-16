import requests
from datetime import datetime, timedelta
import pytz


def calculation(high, low):
    result = ((high - low) / low) * 100
    return result


def format_timestamp(timestamp):
    dt = datetime.fromtimestamp(timestamp / 1000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def check_crossing(date, symbol, timeframe):
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
    
    start_date_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    if start_date_datetime.time() == datetime.strptime("00:00:00", "%H:%M:%S").time():
        start_date_datetime = start_date_datetime.replace(hour=9, minute=30, second=0)
    else:
        start_date_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    ny_timezone = pytz.timezone('America/New_York')
    start_date_datetime = ny_timezone.localize(start_date_datetime)
    end_date_datetime = start_date_datetime + timedelta(hours=interval_mapping[timeframe])
    start_unix_timestamp_milliseconds = int(start_date_datetime.timestamp()) * 1000
    end_unix_timestamp_milliseconds = int(end_date_datetime.timestamp()) * 1000
    
    url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
    response = requests.get(url).json()['results']
    
    previous = None
    active_flag = False
    
    for i in response:
        if active_flag:
            # Case 2: Check for H or L after crossing the middle of the active candle
            avg = (float(i['h']) + float(i['l'])) / 2
            print("Timestamp:", format_timestamp(i['t']))
            # Check if the opening price crosses the average
            if float(i['o']) > avg:
                if float(i['h']) > previous_avg:
                    return '1'
                else:
                    return '0'
            else:
                if float(i['l']) < previous_avg:
                    return '0'
                else:
                    return '1'
                
            active_flag = False  # Reset the active flag after processing
            
        # Case 1: Check for H or L before crossing the middle of the candle
        if float(i['h']) > float(i['l']):
            previous_avg = (float(i['h']) + float(i['l'])) / 2
            active_flag = True  # Set the active flag if H > L
            
        print(i)
    
url = 'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2023-01-09/2023-01-31?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
response = requests.get(url=url).json()['results']

interval_start = 1
interval_end = 2

for index, candle in enumerate(response):
    calculate = calculation(high=float(candle['h']), low=float(candle['l']))
    if interval_start <= calculate <= interval_end:
        print('ACTIVE')
        print("Timestamp:", format_timestamp(candle['t']))
        print(candle)
        dt = datetime.fromtimestamp(candle['t'] / 1000)
        output = check_crossing(date=dt.strftime('%Y-%m-%d %H:%M:%S'), symbol='AAPL', timeframe='1 day')
        print(output)
    else:
        print("Timestamp:", format_timestamp(candle['t']))
        print('NOT ACTIVE')
        print(candle)
        print('2')
