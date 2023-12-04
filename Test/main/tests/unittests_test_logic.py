from datetime import datetime
from unittest.mock import patch
from django.test import TestCase
from ..tasks import shared_async_task

class TestLogic(TestCase):
    @patch('main.tasks.shared_async_task')
    def test_logic_on_twelve_data(self, mock_celery_task):
        expected_output_data = ['0', '0', '0', '0', '0', '1', '0', '1', '0', '0', '2', '1', '1', '1', '0', '1', '1', '0', '0', '1', '1']
        mock_celery_task.return_value = expected_output_data

        data = {
            'symbol': 'AAPL',
            'interval': '1h',
            'bound_up': '0.4',
            'bound_unit_up': '$',
            'bound_low': '0.2',
            'bound_unit_low': '$',
            'start_data': datetime.strptime('2023-11-01', '%Y-%m-%d').strftime('%Y-%m-%d'),
            'end_data': datetime.strptime('2023-11-03', '%Y-%m-%d').strftime('%Y-%m-%d'),  
            'us': 2
        }
        run_task = shared_async_task.delay(data)
        file_path, output_data = run_task.get()
        
        results = []
        for output in output_data:
            results.append(output['output'])

        self.assertEqual(results, expected_output_data)
