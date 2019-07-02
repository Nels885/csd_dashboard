from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from dashboard.models import CsdSoftware, User


class DashboardTestCase(TestCase):

    def setUp(self):
        self.form_data = {
            'jig': 'test', 'new_version': '1', 'link_download': 'test', 'status': 'TEST',
        }
        User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_set_language_vue_is_valid(self):
        for lang in ['fr', 'en']:
            response = self.client.get(reverse('dashboard:set-lang', args={'user_language': lang}))
            self.assertTrue(translation.check_for_language(lang))
            self.assertEqual(response.status_code, 302)

    def test_soft_list_page(self):
        response = self.client.get(reverse('dashboard:soft-list'))
        self.assertEqual(response.status_code, 200)

    def test_soft_add_page_is_disconnected(self):
        response = self.client.get(reverse('dashboard:soft-add'))
        self.assertEqual(response.status_code, 302)

    def test_soft_add_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('dashboard:soft-add'))
        self.assertEqual(response.status_code, 200)

    def test_soft_add_page_is_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_soft = CsdSoftware.objects.count()
        response = self.client.post(reverse('dashboard:soft-add'), self.form_data)
        new_soft = CsdSoftware.objects.count()
        self.assertEqual(new_soft, old_soft + 1)
        self.assertEqual(response.status_code, 200)
