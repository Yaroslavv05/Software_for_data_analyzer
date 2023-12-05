from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from ..views import UserLoginView

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
