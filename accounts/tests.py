from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthTests(TestCase):
    def test_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'john', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe',
            'password1': 'StrongPass123!', 'password2': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='john').exists())

    def test_login(self):
        User.objects.create_user(username='jane', password='StrongPass123!')
        response = self.client.post(reverse('accounts:login'), {'username': 'jane', 'password': 'StrongPass123!'})
        self.assertEqual(response.status_code, 302)
