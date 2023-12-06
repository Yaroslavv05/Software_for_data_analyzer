from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from ..views import UserLoginView, MyFormView, SharesView, SharesPolygonView, SharesYFinanceView
from ..models import Task, UserProfiles
from ..forms import AccountBinanceForm
from unittest.mock import patch

class ChangePasswordViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@gmail.com', first_name='test', password='testpassword')
        self.client.login(username='test@gmail.com', password='testpassword')
        self.url = reverse('change_password')

    def test_change_password_view_post_success(self):
        data = {
            'old_password': 'testpassword',
            'new_password1': 'newtestpassword',
            'new_password2': 'newtestpassword',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn('Пароль успешно изменен.', messages)

    def test_change_password_view_post_failure(self):
        data = {
            'old_password': 'wrongpassword',
            'new_password1': 'newtestpassword',
            'new_password2': 'newtestpassword',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn('Старый пароль неверен.', messages[0])


class ChangeNicknameViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@gmail.com', password='testpassword')
        self.client.login(username='test@gmail.com', password='testpassword')
        self.url = reverse('change_nickname')

    def test_change_nickname_view_post_success(self):
        data = {'new_nickname': 'NewNickName'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn('Ваше имя было измененно на NewNickName', messages[0])
        

class UserLoginViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test@gmail.com', first_name='test', password='testpassword')

    def test_login_view_post_success(self):
        data = {'username': 'test@gmail.com', 'password': 'testpassword'}
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

    def test_login_view_post_failure(self):
        data = {'username': 'test@gmail.com', 'password': 'ggwppassword'}
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.non_field_errors()), 1)
        self.assertEqual(
            form.non_field_errors()[0],
            'Please enter a correct username and password. Note that both fields may be case-sensitive.'
        )

    def test_get_success_url(self):
        view = UserLoginView()
        self.assertEqual(view.get_success_url(), reverse('profile'))


class CancelTaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.user.set_password('testpassword')
        self.user.save()
        self.client.login(username='testuser', password='testpassword')
        self.task = Task.objects.create(user=self.user, is_running=True)

    def test_cancel_task_post_request_pending_state(self):
        url = reverse('cancel_task')
        session = self.client.session
        session['task_id'] = str(self.task.id)
        session.save()

        with patch('main.views.AsyncResult') as mock_async_result:
            mock_result = mock_async_result.return_value
            mock_result.state = 'PENDING'

            response = self.client.post(url)

            self.task.refresh_from_db()
            self.assertEqual(response.status_code, 302)
            self.assertFalse(self.task.is_running)

    def test_cancel_task_post_request_non_pending_state(self):
        url = reverse('cancel_task')
        session = self.client.session
        session['task_id'] = str(self.task.id)
        session.save()

        with patch('main.views.AsyncResult') as mock_async_result:
            mock_result = mock_async_result.return_value
            mock_result.state = 'SUCCESS'

            response = self.client.post(url)

            self.task.refresh_from_db()
            self.assertEqual(response.status_code, 302)
            self.assertFalse(self.task.is_running)


class MyFormViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@gmail.com', password='testpassword')
        Task.objects.create(user=self.user, is_running=True)

    def test_form_valid(self):
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
            'custom_radio_field': '60',
            'use_template': False,
            'save_templates': False,
        }

        self.client.login(username='test@gmail.com', password='testpassword')
        response = self.client.post(reverse('crypto'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(user=self.user, is_running=True).exists())
    
    def test_get_success_url(self):
        view = MyFormView()
        expected_url = reverse('process')
        success_url = view.get_success_url()
        self.assertEqual(success_url, expected_url)


class SharesViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@gmail.com', password='testpassword')
        Task.objects.create(user=self.user, is_running=True)

    def test_form_valid(self):
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
        
        self.client.login(username='test@gmail.com', password='testpassword')
        response = self.client.post(reverse('shares'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(user=self.user, is_running=True).exists())
    
    
    def test_get_success_url(self):
        view = SharesView()
        expected_url = reverse('process_shares')
        success_url = view.get_success_url()
        self.assertEqual(success_url, expected_url)


class SharesPolygonViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@gmail.com', password='testpassword')
        Task.objects.create(user=self.user, is_running=True)

    def test_form_valid(self):
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
        
        self.client.login(username='test@gmail.com', password='testpassword')
        response = self.client.post(reverse('shares_polygon'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(user=self.user, is_running=True).exists())
    
    
    def test_get_success_url(self):
        view = SharesPolygonView()
        expected_url = reverse('process_shares')
        success_url = view.get_success_url()
        self.assertEqual(success_url, expected_url)


class SharesYFinanceViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@gmail.com', password='testpassword')
        Task.objects.create(user=self.user, is_running=True)

    def test_form_valid(self):
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
        
        self.client.login(username='test@gmail.com', password='testpassword')
        response = self.client.post(reverse('shares_yfinance'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(user=self.user, is_running=True).exists())
    
    
    def test_get_success_url(self):
        view = SharesYFinanceView()
        expected_url = reverse('process_shares')
        success_url = view.get_success_url()
        self.assertEqual(success_url, expected_url)


class ProfileViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test@gmail.com', password='testpassword')
        self.client.login(username='test@gmail.com', password='testpassword')

    def test_get_profile_view(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_post_profile_view_valid_data(self):
        data = {
            'name': 'TestProfile',
            'api_key': 'test_api_key',
            'secret_key': 'test_secret_key',
        }
        response = self.client.post(reverse('profile'), data)
        self.assertRedirects(response, reverse('profile'))
        self.assertTrue(UserProfiles.objects.filter(user=self.user, name='TestProfile').exists())

    def test_post_profile_view_invalid_data(self):
        data = {}  # Передайте недопустимые данные для проверки невалидной формы
        response = self.client.post(reverse('profile'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        

class EditProfileViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test@gmail.com', password='testpassword')
        self.client.login(username='test@gmail.com', password='testpassword')
        self.profile = UserProfiles.objects.create(user=self.user, name='OldName')

    def test_get_edit_profile_view(self):
        response = self.client.get(reverse('edit_profile', kwargs={'profile_id': self.profile.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')

    def test_post_edit_profile_view_valid_data(self):
        data = {
            'name': 'NewName',
            'api_key': 'new_api_key',
            'secret_key': 'new_secret_key',
        }
        response = self.client.post(reverse('edit_profile', kwargs={'profile_id': self.profile.id}), data)
        self.assertRedirects(response, reverse('profile'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'NewName')

    def test_post_edit_profile_view_invalid_data(self):
        data = {}
        response = self.client.post(reverse('edit_profile', kwargs={'profile_id': self.profile.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'OldName')

