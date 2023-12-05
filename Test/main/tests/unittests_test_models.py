from django.test import TestCase
from ..models import UserProfiles, TradingData, DataEntry, DateLog, Task, Template
from django.contrib.auth.models import User


class UserProfilesModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.profile = UserProfiles.objects.create(
            user=self.user,
            name='Test Name',
            api_key='test_api_key',
            secret_key='test_secret_key'
        )

    def test_user_profile_creation(self):
        self.assertEqual(self.profile.name, 'Test Name')
        self.assertEqual(self.profile.api_key, 'test_api_key')
        self.assertEqual(self.profile.secret_key, 'test_secret_key')


class DataEntryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.date = DataEntry.objects.create(
            user=self.user,
            date='2023-11-01',
            position='1',
            symbol='BTCUSDT',
            amount_usdt='10',
            leverage='10',
            api_key='test_api_key',
            secret_key='test_secret_key',
            is_completed=True
            
            
        )

    def test_user_profile_creation(self):
        self.assertEqual(self.date.date, '2023-11-01')
        self.assertEqual(self.date.position, '1')
        self.assertEqual(self.date.symbol, 'BTCUSDT')
        self.assertEqual(self.date.amount_usdt, '10')
        self.assertEqual(self.date.leverage, '10')
        self.assertEqual(self.date.api_key, 'test_api_key')
        self.assertEqual(self.date.secret_key, 'test_secret_key')
        self.assertEqual(self.date.is_completed, True)


class DateLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.log = DateLog.objects.create(
            date='2023-11-01',
            task_id='test_task_id',
        )

    def test_user_profile_creation(self):
        self.assertEqual(self.log.date, '2023-11-01')
        self.assertEqual(self.log.task_id, 'test_task_id')


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.task = Task.objects.create(
            user=self.user,
            is_running=True,
        )

    def test_user_profile_creation(self):
        self.assertEqual(self.task.is_running, True)


class TemplateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.template = Template.objects.create(
            user=self.user,
            name_exchange='Binance',
            name='test_name',
            choice='in',
            api='test_api',
            symbol='BTCUSDT',
            interval='4 hour',
            bound_up = '0.4',
            bound_unit_up = '$',
            bound_low = '0.05',
            bound_unit_low = '%',
            start_date = '2023-11-01',
            end_date = '2023-12-01',
            min_interval = '60'
        )

    def test_user_profile_creation(self):
        self.assertEqual(self.template.name_exchange, 'Binance')
        self.assertEqual(self.template.name, 'test_name')
        self.assertEqual(self.template.choice, 'in')
        self.assertEqual(self.template.api, 'test_api')
        self.assertEqual(self.template.symbol, 'BTCUSDT')
        self.assertEqual(self.template.interval, '4 hour')
        self.assertEqual(self.template.bound_up, '0.4')
        self.assertEqual(self.template.bound_unit_up, '$')
        self.assertEqual(self.template.bound_low, '0.05')
        self.assertEqual(self.template.bound_unit_low, '%')
        self.assertEqual(self.template.start_date, '2023-11-01')
        self.assertEqual(self.template.end_date, '2023-12-01')
        self.assertEqual(self.template.min_interval, '60')