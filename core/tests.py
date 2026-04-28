from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class PermissionTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)

    def test_admin_panel_permissions(self):
        user = User.objects.create_user(username='x', password='StrongPass123!')
        self.client.login(username='x', password='StrongPass123!')
        response = self.client.get(reverse('dashboard:admin_panel'))
        self.assertEqual(response.status_code, 302)
