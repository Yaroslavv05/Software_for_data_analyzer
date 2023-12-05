from django.test import TestCase
from ..forms import UserLoginForm, PasswordChangeForm, FirstNameChangeForm, AccountBinanceForm, SharesYFinanceForm, SharesPolygonForm, SharesForm, MyForm, EditTemplatePolygonForm, EditTemplateTwelveDataForm, EditTemplateBinancesForm
from django.contrib.auth.models import User
from ..models import Template, UserProfiles
from django.core.files.uploadedfile import SimpleUploadedFile


class UserLoginFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@gmail.com', password='test_password')

    def test_login_form(self):
        form_data = {
            'username': 'test@gmail.com',
            'password': 'test_password'
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())


    def test_login_form_invalid(self):
        form_data = {
            'username': 'ggwp@gmail.com',
            'password': 'test_password'
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())


class PasswordChangeFormTest(TestCase):
    def test_password_change_form(self):
        form_data = {
            'old_password': 'test_old_password',
            'new_password1': 'test_new_password',
            'new_password2': 'test_new_password'
         }
        form = PasswordChangeForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_change_form_inalid(self):
        form_data = {
            'old_password': 'test_old_password',
            'new_password1': 'test_new_password',
            'new_password2': ''
         }
        form = PasswordChangeForm(data=form_data)
        self.assertFalse(form.is_valid())


class FirstNameChangeFormTest(TestCase):
    def test_first_name_change_form(self):
        form_data = {
            'new_nickname': 'Test_nickname'
         }
        form = FirstNameChangeForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_first_name_change_form_invalid(self):
        form_data = {
            'new_nickname': ''
         }
        form = FirstNameChangeForm(data=form_data)
        self.assertFalse(form.is_valid())


class AccountBinanceFormTest(TestCase):
    def test_account_binance_form(self):
        form_data = {
            'name': 'test_name',
            'api_key': 'test_api_key',
            'secret_key': 'test_secret_key'
         }
        form = AccountBinanceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_account_binance_form_invalid(self):
        form_data = {
            'name': 'test_name',
            'api_key': 'test_api_key',
            'secret_key': ''
         }
        form = AccountBinanceForm(data=form_data)
        self.assertFalse(form.is_valid())


class SharesYFinanceFormTest(TestCase):
    def test_shares_yfinance_form_valid(self):
        form_data = {
            'symbol': 'AAPL',
            'interval': '1d',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '90',
            'bound_unit_low': '$',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'custom_radio_field': '60'
        }
        form = SharesYFinanceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_shares_yfinance_form_invalid(self):
        form_data = {
            'symbol': '',
            'interval': '1m',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '90',
            'bound_unit_low': '$',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'custom_radio_field': '60'
        }
        form = SharesYFinanceForm(data=form_data)
        self.assertFalse(form.is_valid())


class SharesPolygonFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.template1 = Template.objects.create(user=self.user, name_exchange='Polygon', name='Template 1')
        self.template2 = Template.objects.create(user=self.user, name_exchange='Polygon', name='Template 2')

    def test_shares_polygon_form_creation(self):
        form = SharesPolygonForm(user=self.user)
        self.assertIsInstance(form, SharesPolygonForm)

    def test_shares_polygon_form_valid(self):
        form_data = {
            'choice': 'pre',
            'symbol': 'AAPL',
            'interval': '1 minute',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '90',
            'bound_unit_low': '$',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'use_templates': False,
            'custom_radio_field': '1'
        }
        form = SharesPolygonForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_shares_polygon_form_invalid(self):
        form_data = {
            'choice': 'in',
            'symbol': 'AAPL',
            'interval': '',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '90',
            'bound_unit_low': '$',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'use_templates': False,
            'custom_radio_field': '1'
        }
        form = SharesPolygonForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())


class SharesFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.template1 = Template.objects.create(user=self.user, name_exchange='TwelveData', name='Template 1')
        self.template2 = Template.objects.create(user=self.user, name_exchange='TwelveData', name='Template 2')

    def test_shares_form_creation(self):
        form = SharesForm(user=self.user)
        self.assertIsInstance(form, SharesForm)

    def test_shares_form_valid(self):
        form_data = {
            'symbol': 'AAPL',
            'interval': '1min',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '90',
            'bound_unit_low': '$',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'use_templates': False,
            'custom_radio_field': '60'
        }
        form = SharesForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_shares_form_invalid(self):
        form_data = {
            'symbol': 'AAPL',
            'interval': '',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '90',
            'bound_unit_low': '$',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'use_templates': False,
            'custom_radio_field': '60'
        }
        form = SharesForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())


class MyFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.template1 = Template.objects.create(user=self.user, name_exchange='Binance', name='Template 1')
        self.template2 = Template.objects.create(user=self.user, name_exchange='Binance', name='Template 2')

    def test_my_form_creation(self):
        form = MyForm(user=self.user)
        self.assertIsInstance(form, MyForm)

    def test_shares_form_valid(self):
        form_data = {
            'symbol': 'BTCUSDT',
            'interval': 4,
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '90',
            'bound_unit_low': '$',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'use_templates': False,
            'custom_radio_field': '60'
        }
        form = MyForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_my_form_invalid(self):
        form_data = {
            'symbol': 'BTCUSDT',
            'interval': '',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '90',
            'bound_unit_low': '$',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'use_templates': False,
            'custom_radio_field': '60'
        }
        form = MyForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        

class EditTemplatePolygonFormTest(TestCase):
    def test_edit_template_polygon_form_valid(self):
        form_data = {
            'name': 'Test Template',
            'choice': 'pre',
            'symbol': 'AAPL',
            'interval': '1 minute',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '50',
            'bound_unit_low': '%',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'custom_radio_field': '60'
        }
        form = EditTemplatePolygonForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_edit_template_polygon_form_invalid(self):
        form_data = {
            'name': 'Test Template',
            'choice': 'pre',
            'symbol': 'AAPL',
            'interval': '1 minute',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '50',
            'bound_unit_low': '%',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'custom_radio_field': ''
        }
        form = EditTemplatePolygonForm(data=form_data)
        self.assertFalse(form.is_valid())

class EditTemplateTwelveDataFormTest(TestCase):
    def test_edit_template_twelve_data_form_valid(self):
        form_data = {
            'name': 'Test Template',
            'symbol': 'AAPL',
            'interval': '1min',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '50',
            'bound_unit_low': '%',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'custom_radio_field': '60'
        }
        form = EditTemplateTwelveDataForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_edit_template_twelve_data_form_invalid(self):
        form_data = {
            'name': 'Test Template',
            'symbol': 'AAPL',
            'interval': '1min',
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '50',
            'bound_unit_low': '%',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'custom_radio_field': ''
        }
        form = EditTemplateTwelveDataForm(data=form_data)
        self.assertFalse(form.is_valid())


class EditTemplateBinancesFormTest(TestCase):
    def test_edit_template_binances_form_valid(self):
        form_data = {
            'name': 'Test Template',
            'symbol': 'BTCUSDT',
            'interval': 4,
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '50',
            'bound_unit_low': '%',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'custom_radio_field': '60'
        }
        form = EditTemplateBinancesForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    
    def test_edit_template_binances_form_invalid(self):
        form_data = {
            'name': 'Test Template',
            'symbol': 'BTCUSDT',
            'interval': 4,
            'bound_up': '100',
            'bound_unit_up': '$',
            'bound_low': '50',
            'bound_unit_low': '%',
            'start_data_0': '2023-01-01',
            'start_data_1': '00:00',
            'end_data_0': '2023-01-05',
            'end_data_1': '23:59',
            'custom_radio_field': ''
        }
        form = EditTemplateBinancesForm(data=form_data)
        self.assertFalse(form.is_valid())
