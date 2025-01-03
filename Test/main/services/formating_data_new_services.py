import requests
from datetime import datetime, timezone, timedelta
import pytz
import openpyxl
import os
from ..models import DateLog

class FormatingDataServiceNew:
    def __init__(self, symbol, timeframe, interval_start, interval_end, start_date, end_date, api_key, asset_type):
        self.symbol = symbol
        self.interval_start = interval_start
        self.interval_end = interval_end
        self.start_date = start_date
        self.end_date = end_date
        self.api_key = api_key
        self.timeframe = timeframe
        self.asset_type = asset_type


    def check_crossing_low(self, avg, previous_high, previous_low, date, symbol, timeframe):
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
        if self.asset_type == 'currency':
            url = f'https://api.polygon.io/v2/aggs/ticker/C:{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        else:
            url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        
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
                return output, status, crossed_avg 
            elif crossed_avg and candle['l'] < previous_low:
                output = '0'
                status = 'ACTIVE'
                return output, status, crossed_avg 

        return '1/0', 'ACTIVE', crossed_avg 


    def check_crossing_low_or_high(self, avg, previous_high, previous_low, date, symbol, timeframe):
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
        if self.asset_type == 'currency':
            url = f'https://api.polygon.io/v2/aggs/ticker/C:{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        else:
            url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        
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
                return output, status, crossed_avg
            elif crossed_avg == False and candle['h'] > previous_high:
                output = '2'
                status = 'NOT ACTIVE'
                return output, status, crossed_avg
            elif crossed_avg and candle['h'] > previous_high:
                output = '1'
                status = 'ACTIVE'
                return output, status, crossed_avg
            elif crossed_avg and candle['l'] < previous_low:
                output = '0'
                status = 'ACTIVE'
                return output, status, crossed_avg 

        return '1/0', 'ACTIVE', crossed_avg
    
    
    def check_crossing_avg(self, avg, previous_high, previous_low, date, symbol, timeframe):
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
        if self.asset_type == 'Currency':
            url = f'https://api.polygon.io/v2/aggs/ticker/C:{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        else:
            url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        
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

        return '1/0', 'ACTIVE', crossed_avg


    def check_crossing_high(self, avg, previous_high, previous_low, date, symbol, timeframe):
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
        if self.asset_type == 'currency':
            url = f'https://api.polygon.io/v2/aggs/ticker/C:{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        else:
            url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_unix_timestamp_milliseconds}/{end_unix_timestamp_milliseconds}?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
        
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


    def is_valid_time(self, time):
            return (time.hour == 9 and time.minute >= 30) or (9 < time.hour < 15) or (time.hour == 15 and time.minute <= 30)

    def convert_unix_to_datetime_for_4h_candles(self, unix_timestamp):
        dt_object = datetime.fromtimestamp(unix_timestamp / 1000.0, tz=timezone.utc)
        dt_object = dt_object.astimezone(timezone(timedelta(hours=-5)))
        return dt_object.strftime('%Y-%m-%d %H:%M:%S')


    def convert_unix_to_datetime_for_1h_candles(self, unix_timestamp):
        dt_object = datetime.fromtimestamp(unix_timestamp / 1000.0, tz=timezone.utc)
        ny_timezone = pytz.timezone('America/New_York')
        dt_object = dt_object.astimezone(ny_timezone)
        return dt_object.strftime('%Y-%m-%d %H:%M:%S')


    def create_4h_candles(self, data):
        print(data)
        candles_4h = []

        current_candle = None

        for entry in data:
            entry_time = datetime.strptime(entry['t'], '%Y-%m-%d %H:%M:%S')

            if current_candle is None:
                current_candle = {
                    'o': entry['o'],
                    'h': entry['h'],
                    'l': entry['l'],
                    'c': entry['c'],
                    'v': entry['v'],
                    't': entry_time.replace(minute=30, second=0),
                    'n': entry['n']
                }
            else:
                if entry_time >= current_candle['t'] + timedelta(hours=4):
                    current_candle['t'] = current_candle['t'].strftime('%Y-%m-%d %H:%M:%S')
                    candles_4h.append(current_candle)
                    current_candle = {
                        'o': entry['o'],
                        'h': entry['h'],
                        'l': entry['l'],
                        'c': entry['c'],
                        'v': entry['v'],
                        't': entry_time.replace(minute=30, second=0),
                        'n': entry['n']
                    }
                else:
                    current_candle['h'] = max(current_candle['h'], entry['h'])
                    current_candle['l'] = min(current_candle['l'], entry['l'])
                    current_candle['c'] = entry['c']
                    current_candle['v'] += entry['v']
                    current_candle['n'] += entry['n']

        if current_candle is not None:
            current_candle['t'] = current_candle['t'].strftime('%Y-%m-%d %H:%M:%S')
            candles_4h.append(current_candle)

        return candles_4h
    
    
    def create_1h_candles(self, data):
        print(data)
        candles_1h = []
        current_interval = {} 

        for candle in data:
            candle_date = datetime.strptime(candle['t'], '%Y-%m-%d %H:%M:%S')

            if not current_interval: 
                current_interval = {
                    't': candle_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'o': candle['o'],
                    'c': candle['c'],
                    'h': candle['h'],
                    'l': candle['l'],
                    'n': candle['n'],
                    'v': candle['v']
                }
            else:
                current_interval_date = datetime.strptime(current_interval['t'], '%Y-%m-%d %H:%M:%S')
                time_difference = (candle_date - current_interval_date).total_seconds()
                if time_difference < 3600:
                    current_interval['c'] = candle['c']
                    current_interval['h'] = max(current_interval['h'], candle['h'])
                    current_interval['l'] = min(current_interval['l'], candle['l'])
                    current_interval['n'] += candle['n']
                    current_interval['v'] += candle['v']
                else:
                    candles_1h.append(current_interval)
                    current_interval = {
                        't': candle_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'o': candle['o'],
                        'c': candle['c'],
                        'h': candle['h'],
                        'l': candle['l'],
                        'n': candle['n'],
                        'v': candle['v']
                    }

        if current_interval:
            candles_1h.append(current_interval)

        return candles_1h
            


    def split_into_3_month_intervals(self, start_date, end_date):
        intervals = []
        current_date = start_date
        while current_date < end_date:
            next_date = current_date + timedelta(days=90)
            if next_date > end_date:
                next_date = end_date
            intervals.append((current_date, next_date))
            current_date = next_date
        return intervals

    def output(self):
        intervals = self.split_into_3_month_intervals(datetime.strptime(self.start_date, '%Y-%m-%d').date(), datetime.strptime(self.end_date, '%Y-%m-%d').date())

        results = []
        for i, interval in enumerate(intervals, start=1):
            if self.asset_type == 'currency':
                url = f'https://api.polygon.io/v2/aggs/ticker/C:{self.symbol}/range/30/minute/{interval[0].strftime("%Y-%m-%d")}/{interval[1].strftime("%Y-%m-%d")}?adjusted=true&sort=asc&limit=50000&apiKey={self.api_key}'
            else:
                url = f'https://api.polygon.io/v2/aggs/ticker/{self.symbol}/range/30/minute/{interval[0].strftime("%Y-%m-%d")}/{interval[1].strftime("%Y-%m-%d")}?adjusted=true&sort=asc&limit=50000&apiKey={self.api_key}'
            response = requests.get(url)
            results.append(response.json()['results'])

        print(f'RESULTS {results}')
        data = []
        for result in results:
            for j in result:
                if self.timeframe == '1 hour':
                    j['t'] = self.convert_unix_to_datetime_for_1h_candles(j['t'])
                    time = datetime.strptime(j['t'], '%Y-%m-%d %H:%M:%S')
                    if self.is_valid_time(time):
                        data.append(j)
                elif self.timeframe == '4 hour':
                    j['t'] = self.convert_unix_to_datetime_for_4h_candles(j['t'])
                    time = datetime.strptime(j['t'], '%Y-%m-%d %H:%M:%S')
                    if self.is_valid_time(time):
                        data.append(j)
        
        if self.timeframe == '4 hour':
            candles = self.create_4h_candles(data)
        elif self.timeframe == '1 hour':
            candles = self.create_1h_candles(data)
            
        self.output_data = []

        for i in range(len(candles) - 1):
            previous_candle = candles[i - 1]
            candle = candles[i]
            next_candle = candles[i + 1]
            parsed_date = datetime.strptime(candle['t'], "%Y-%m-%d %H:%M:%S")
            DateLog.objects.create(date=parsed_date.date(), task_id='1')
            print(candle)
            
            
            time = candle['t']
            open_price = candle['o']
            high = candle['h']
            low = candle['l']
            close = candle['c'] 
            volume = candle['v']
            trade = candle['n']
            next_open = next_candle['o']
            amplitude = ((high - low) / low) * 100
            print(candle)
            
            next_time = next_candle['t']
            if self.interval_start <= amplitude <= self.interval_end:
                avg = (high + low) / 2
                next_high = next_candle['h']
                next_low = next_candle['l']
                if next_open < low or next_open > high:
                    status = 'NOT ACTIVE'
                    output = '2'
                    print(status, output)
                elif (high < next_high and next_low > avg) or high == next_high:
                    print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
                    output, status, crossed_avg  = self.check_crossing_avg(avg, high, low, next_time, self.symbol, self.timeframe)
                    print(status, output, crossed_avg)
                    if output == '1/0' and status == 'ACTIVE' and crossed_avg == True:
                        previous_high = high
                        previous_low = low
                        for j in candles[i:-1]:
                            if j['o'] < previous_low:
                                status = 'ACTIVE'
                                output = '0'
                                print(status, output)
                                break
                            elif j['o'] > previous_high:
                                status = 'ACTIVE'
                                output = '1'
                                print(status, output)
                                break
                            elif j['h'] > previous_high:
                                status = 'ACTIVE'
                                output = '1'
                                print(status, output)
                                break
                            elif j['l'] < previous_low:
                                status = 'ACTIVE'
                                output = '0'
                                print(status, output)
                                break
                    elif output == '1/0' and status == 'ACTIVE' and crossed_avg == False:
                        status = 'NOT ACTIVE'
                        output = '2'
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
                    output, status, crossed_avg  = self.check_crossing_low_or_high(avg, high, low, next_time, self.symbol, self.timeframe)
                    print(status, output)
                    if output == '1/0' and status == 'ACTIVE' and crossed_avg == True:
                        previous_high = high
                        previous_low = low
                        for j in candles[i:-1]:
                            if j['o'] < previous_low:
                                status = 'ACTIVE'
                                output = '0'
                                print(status, output)
                                break
                            elif j['o'] > previous_high:
                                status = 'ACTIVE'
                                output = '1'
                                print(status, output)
                                break
                            elif j['h'] > previous_high:
                                status = 'ACTIVE'
                                output = '1'
                                print(status, output)
                                break
                            elif j['l'] < previous_low:
                                status = 'ACTIVE'
                                output = '0'
                                print(status, output)
                                break
                    elif output == '1/0' and status == 'ACTIVE' and crossed_avg == False:
                        status = 'NOT ACTIVE'
                        output = '2'
                elif next_high > avg and next_low < avg and next_high < high and next_low > low:
                    print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
                    previous_high = high
                    previous_low = low
                    for j in candles[i:-1]:
                        if j['o'] < previous_low:
                            status = 'ACTIVE'
                            output = '0'
                            print(status, output)
                            break
                        elif j['o'] > previous_high:
                            status = 'ACTIVE'
                            output = '1'
                            print(status, output)
                            break
                        elif j['h'] > previous_high:
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
                    output, status, crossed_avg  = self.check_crossing_high(avg, high, low, next_time, self.symbol, self.timeframe)
                    print(status, output)
                    if output == '1/0' and status == 'ACTIVE' and crossed_avg == True:
                        previous_high = high
                        previous_low = low
                        for j in candles[i:-1]:
                            if j['o'] < previous_low:
                                status = 'ACTIVE'
                                output = '0'
                                print(status, output)
                                break
                            elif j['o'] > previous_high:
                                status = 'ACTIVE'
                                output = '1'
                                print(status, output)
                                break
                            elif j['h'] > previous_high:
                                status = 'ACTIVE'
                                output = '1'
                                print(status, output)
                                break
                            elif j['l'] < previous_low:
                                status = 'ACTIVE'
                                output = '0'
                                print(status, output)
                                break
                    elif output == '1/0' and status == 'ACTIVE' and crossed_avg == False:
                        status = 'NOT ACTIVE'
                        output = '2'
                elif low > next_low and next_high > avg:
                    print(f'high - {high}\next_high - {next_high}\next_low - {next_low}\navg - {avg}\nlow - {low}')
                    output, status, crossed_avg = self.check_crossing_low(avg, high, low, next_time, self.symbol, self.timeframe)
                    print(status, output)
                    if output == '1/0' and status == 'ACTIVE' and crossed_avg == True:
                        previous_high = high
                        previous_low = low
                        for j in candles[i:-1]:
                            if j['o'] < previous_low:
                                status = 'ACTIVE'
                                output = '0'
                                print(status, output)
                                break
                            elif j['o'] > previous_high:
                                status = 'ACTIVE'
                                output = '1'
                                print(status, output)
                                break
                            elif j['h'] > previous_high:
                                status = 'ACTIVE'
                                output = '1'
                                print(status, output)
                                break
                            elif j['l'] < previous_low:
                                status = 'ACTIVE'
                                output = '0'
                                print(status, output)
                                break
                    elif output == '1/0' and status == 'ACTIVE' and crossed_avg == False:
                        status = 'NOT ACTIVE'
                        output = '2'
                else:
                    status = 'NOT ACTIVE'
                    output = '2'
                    print(status, output)
            else:
                status = 'NOT ACTIVE'
                output = '2'
                print(status, output)
                
            self.output_data.append({
                'time': candle['t'],
                'status': status,
                'output': output,
                'open': candle['o'],
                'close': candle['c'],
                'high': candle['h'],
                'low': candle['l'],
                'trade': candle['n'],
                'volume': candle['v']
            })
            import time
            time.sleep(0.01)
            # try:
            #     date_log = DateLog.objects.get(task_id='1')
            #     date_log.delete()
            # except:
            #     print('Ничего не найденно по такому ID')

        return self.output_data
    
    
    def save_output_to_excel(self):
        wb = openpyxl.Workbook()
        ws = wb.active

        headers = ['Date', 'Status', 'Output', 'Open', 'Close', 'High', 'Low', 'Trade', 'Volume']
        for col_index, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_index, value=header)

        output_data = self.output()
        for item in output_data:
            row_data = [item['time'],item['status'], item['output'], item['open'], item['close'], item['high'], item['low'], item['trade'], item['volume']]
            ws.append(row_data)
        file = f'{self.symbol}_{self.timeframe}_{self.interval_start}%_{self.interval_end}%_{self.start_date}_{self.end_date}(Polygon).xlsx'
        file = file.replace(':', '_').replace('?', '_').replace(' ', '_')
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'..\\..\\{file}')
        with open(file_path, 'wb') as file:
            wb.save(file)
        
        return file_path, output_data