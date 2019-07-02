from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardTestCase(TestCase):

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')

    def test_set_language_vue_is_valid(self):
        for lang in ['fr', 'en']:
            response = self.client.get(reverse('dashboard:set_lang', args={'user_language': lang}))
            self.assertTrue(translation.check_for_language(lang))
            self.assertEqual(response.status_code, 302)
