from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from ..views import UserLoginView


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

