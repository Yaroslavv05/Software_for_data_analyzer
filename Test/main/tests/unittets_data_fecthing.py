import unittest
import requests


def calculate_output(i, bound_check_up, bound_check_low):
    if float(i['high']) - float(i['open']) >= bound_check_up and float(i['open']) - float(i['low']) >= bound_check_low:
        return controversial(open_price=float(i['open']), bound_up=bound_check_up, bound_low=bound_check_low)
    elif float(i['high']) - float(i['open']) >= bound_check_up:
        return '1'
    elif float(i['open']) - float(i['low']) >= bound_check_low:
        return '0'
    else:
        return '2'


def controversial(open_price, bound_up, bound_low):    
    response = requests.get(
        f"https://api.twelvedata.com/time_series?apikey=7e1f42d9a4f743749ffa9e77958e06a4&interval=1min&symbol=AAPL&timezone=exchange&start_date=2023-11-01 00:00:00&end_date=2023-11-03 00:00:00&format=JSON")
    try:
        d = response.json()['values']
    except:
        return '3'

    for j in d[::-1]:
        if float(j['high']) - open_price >= bound_up:
            return '1'
        elif open_price - float(j['low']) >= bound_low:
            return '0'


class TestBuisnesLogickDA(unittest.TestCase):

    def test_output_1(self):
        i = {'high': '10', 'open': '7', 'low': '6'}
        bound_check_up = 3
        bound_check_low = 2
        self.assertEqual(calculate_output(i, bound_check_up, bound_check_low), '1')

    def test_output_0(self):
        i = {'high': '9', 'open': '7', 'low': '5'}
        bound_check_up = 3
        bound_check_low = 2
        self.assertEqual(calculate_output(i, bound_check_up, bound_check_low), '0')

    def test_output_2(self):
        i = {'high': '7', 'open': '8', 'low': '6'}
        bound_check_up = 1
        bound_check_low = 3
        self.assertEqual(calculate_output(i, bound_check_up, bound_check_low), '2')
    
    def test_real_data(self):
        results = []
        data = [
            {'datetime': '2023-11-02 15:30:00', 'open': '177.23500', 'high': '177.78000', 'low': '177.17000', 'close': '177.78000', 'volume': '9466400'},
            {'datetime': '2023-11-02 14:30:00', 'open': '177.30209', 'high': '177.72000', 'low': '177.19000', 'close': '177.23000', 'volume': '7714957'},
            {'datetime': '2023-11-02 13:30:00', 'open': '177.08000', 'high': '177.61000', 'low': '177.08000', 'close': '177.31000', 'volume': '5633333'},
            {'datetime': '2023-11-02 12:30:00', 'open': '176.98000', 'high': '177.31500', 'low': '176.78000', 'close': '177.08800', 'volume': '5823586'},
            {'datetime': '2023-11-02 11:30:00', 'open': '176.77000', 'high': '177.10001', 'low': '176.41000', 'close': '176.98000', 'volume': '6002941'},
            {'6datetime': '2023-11-02 10:30:00', 'open': '176.88000', 'high': '177.66000', 'low': '176.62000', 'close': '176.77400', 'volume': '9566990'},
            {'datetime': '2023-11-02 09:30:00', 'open': '175.52000', 'high': '177.09000', 'low': '175.46001', 'close': '176.87000', 'volume': '12660603'},
            {'datetime': '2023-11-01 15:30:00', 'open': '173.91000', 'high': '174.23000', 'low': '173.61000', 'close': '173.92000', 'volume': '7686378'},
            {'datetime': '2023-11-01 14:30:00', 'open': '172.62500', 'high': '174.17000', 'low': '172.10001', 'close': '173.91000', 'volume': '10340415'},
            {'datetime': '2023-11-01 13:30:00', 'open': '172.16000', 'high': '172.71001', 'low': '171.91000', 'close': '172.61000', 'volume': '5184502'},
            {'datetime': '2023-11-01 12:30:00', 'open': '171.91000', 'high': '172.38000', 'low': '171.63000', 'close': '172.16200', 'volume': '3882871'},
            {'datetime': '2023-11-01 11:30:00', 'open': '171.42999', 'high': '172.00000', 'low': '171.19501', 'close': '171.89999', 'volume': '3513567'},
            {'datetime': '2023-11-01 10:30:00', 'open': '171.83000', 'high': '172.08000', 'low': '171.00000', 'close': '171.42999', 'volume': '6770956'},
            {'datetime': '2023-11-01 09:30:00', 'open': '171.00000', 'high': '171.97000', 'low': '170.12000', 'close': '171.83000', 'volume': '10298739'},
        ]
        for i in data[::-1]:
            output = calculate_output(i, bound_check_up=0.4, bound_check_low=0.2)
            results.append(output)
        self.assertEqual(results, ['1', '1', '1', '2', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0'][::-1])
        
if __name__ == '__main__':
    unittest.main()

    