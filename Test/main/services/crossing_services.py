from binance.client import Client
from datetime import datetime, timedelta


def check_crossing_low_crypto(avg, previous_high, previous_low, date, symbol, timeframe):
    try:
        client = Client()
        interval = Client.KLINE_INTERVAL_1MINUTE
        start_date = date
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date_datetime = start_date_datetime + timedelta(hours=timeframe)
        klines = client.futures_historical_klines(symbol, interval, start_date_datetime.strftime('%Y-%m-%d %H:%M:%S'), end_date_datetime.strftime('%Y-%m-%d %H:%M:%S'))
        response = []
        for kline in klines:
            time = datetime.fromtimestamp(kline[0] / 1000)
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
            response.append({
                't': formatted_time,
                'o': float(kline[1]),
                'h': float(kline[2]),
                'l': float(kline[3]),
            })
        
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
                return output, status, crossed_avg 
            elif crossed_avg and candle['l'] < previous_low:
                output = '0'
                status = 'ACTIVE'
                return output, status, crossed_avg 
    except Exception as e:
        print(e) 
    return '1/0', 'ACTIVE', crossed_avg


def check_crossing_low_or_high_crypto(avg, previous_high, previous_low, date, symbol, timeframe):
    try:
        client = Client()
        interval = Client.KLINE_INTERVAL_1MINUTE
        start_date = date
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date_datetime = start_date_datetime + timedelta(hours=timeframe)
        klines = client.futures_historical_klines(symbol, interval, start_date_datetime.strftime('%Y-%m-%d %H:%M:%S'), end_date_datetime.strftime('%Y-%m-%d %H:%M:%S'))
        response = []
        for kline in klines:
            time = datetime.fromtimestamp(kline[0] / 1000)
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
            response.append({
                't': formatted_time,
                'o': float(kline[1]),
                'h': float(kline[2]),
                'l': float(kline[3]),
            })
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
    except Exception as e:
        print(e)   


def check_crossing_avg_crypto(avg, previous_high, previous_low, date, symbol, timeframe):
        crossed_avg = False
        try:
            client = Client()
            interval = Client.KLINE_INTERVAL_1MINUTE
            start_date = date
            start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            end_date_datetime = start_date_datetime + timedelta(hours=timeframe)
            klines = client.futures_historical_klines(symbol, interval, start_date_datetime.strftime('%Y-%m-%d %H:%M:%S'), end_date_datetime.strftime('%Y-%m-%d %H:%M:%S'))
            response = []
            for kline in klines:
                time = datetime.fromtimestamp(kline[0] / 1000)
                formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
                response.append({
                    't': formatted_time,
                    'o': float(kline[1]),
                    'h': float(kline[2]),
                    'l': float(kline[3]),
                })


            for i, candle in enumerate(response):
                print(candle)
                if crossed_avg == False and candle['o'] < avg and candle['h'] > avg:
                    crossed_avg = True
                    print('Было пересечение средины')
                elif crossed_avg == False and candle['o'] > avg and candle['l'] < avg:
                    crossed_avg = True
                    print('Было пересечение средины')
        except Exception as e:
            print(e) 
        return '1/0', 'ACTIVE', crossed_avg


def check_crossing_high_crypto(avg, previous_high, previous_low, date, symbol, timeframe):
    try:
        client = Client()
        interval = Client.KLINE_INTERVAL_1MINUTE
        start_date = date
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date_datetime = start_date_datetime + timedelta(hours=timeframe)
        klines = client.futures_historical_klines(symbol, interval, start_date_datetime.strftime('%Y-%m-%d %H:%M:%S'), end_date_datetime.strftime('%Y-%m-%d %H:%M:%S'))
        response = []
        for kline in klines:
            time = datetime.fromtimestamp(kline[0] / 1000)
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
            response.append({
                't': formatted_time,
                'o': float(kline[1]),
                'h': float(kline[2]),
                'l': float(kline[3]),
            })
        crossed_avg = False

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
            
    except Exception as e:
        print(e)
    return '1/0', 'ACTIVE', crossed_avg