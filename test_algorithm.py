import requests

def calculation(high, low):
    result = ((high - low) / low) * 100
    return result

def check_crossing(previous, current):
    avarage = (float(previous['h']) + float(previous['l'])) / 2
    if float(current['h']) > avarage and float(current['l']) < avarage:
        return '1/0'
    elif float(current['h']) > avarage:
        return '1'
    elif float(current['l']) < avarage:
        return '0'

url = 'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2023-01-09/2023-01-31?adjusted=true&sort=asc&limit=50000&apiKey=EH2vpdYrp_dt3NHfcTjPhu0JOKKw0Lwz'
response = requests.get(url=url).json()['results']

previous_candle = None
interval_start = 1
interval_end = 2

for index, candle in enumerate(response):
    calculate = calculation(high=float(candle['h']), low=float(candle['l']))
    # print(candle)
    if calculate >= interval_start and calculate <= interval_end:
        print('ACTIVE')
        if previous_candle is not None:
            print('CURRENT', candle)
            print('PREVIOUS', previous_candle)
            cross_result = check_crossing(previous_candle, candle)
            print('RESULT', cross_result)
        else:
            print("No previous candle for comparison.")
            
    else:
        print('NOT ACTIVE')
        print(candle)
    
    previous_candle = candle if index != len(response) - 1 else None
