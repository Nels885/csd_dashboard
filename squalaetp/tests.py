from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class DashboardTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('toto', 'toto@bibi.com', 'totopassword')
        user.save()

    def test_xelon_table_page(self):
        response = self.client.get(reverse('squalaetp:xelon'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_table_page_is_disconnected(self):
        response = self.client.get(reverse('squalaetp:corvet'))
        self.assertEqual(response.status_code, 302)

    def test_corvet_table_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('squalaetp:corvet'))
        self.client.logout()
        self.assertEqual(response.status_code, 200)
