from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User, Group

from squalaetp.models import Xelon


class DashboardTestCase(TestCase):

    def setUp(self):
        self.vin = 'VF3ABCDEF12345678'
        admin = User.objects.create_user(username='admin', email='admin@admin.com', password='adminpassword')
        admin.is_staff = True
        admin.save()
        user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        user.save()
        xelon = Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                                     modele_vehicule='peugeot')
        self.xelonId = str(xelon.id)
        self.redirectUrl = reverse('index')

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_set_language_view_is_valid(self):
        for lang in ['fr', 'en']:
            response = self.client.get(reverse('dashboard:set-lang', args={'user_language': lang}),
                                       HTTP_REFERER=self.redirectUrl)
            self.assertTrue(translation.check_for_language(lang))
            self.assertRedirects(response, self.redirectUrl, status_code=302)

    def test_user_profile_is_disconnected(self):
        response = self.client.get(reverse('dashboard:user-profile'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/profile/', status_code=302)

    def test_user_profile_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('dashboard:user-profile'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_is_not_staff(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('dashboard:signup'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/signup/', status_code=302)

    def test_signup_page_is_staff(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('dashboard:signup'))
        self.assertEqual(response.status_code, 200)

    def test_search_is_disconnected(self):
        response = self.client.get(reverse('dashboard:search'), {'query': 'null', 'select': 'xelon'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/search/%3Fquery%3Dnull%26select%3Dxelon')

    def test_search_is_not_found(self):
        self.client.login(username='toto', password='totopassword')
        for value in ['null', 'A1234567890', 'azertyuiop123456789', 'AZERTIOP']:
            response = self.client.get(reverse('dashboard:search'), {'query': 'null', 'select': 'xelon'},
                                       HTTP_REFERER=self.redirectUrl)
            self.assertRedirects(response, self.redirectUrl, status_code=302)

    def test_search_is_not_value(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('dashboard:search'), HTTP_REFERER=self.redirectUrl)
        self.assertRedirects(response, self.redirectUrl, status_code=302)

    def test_search_vin_is_valid(self):
        self.client.login(username='toto', password='totopassword')
        for value in [self.vin, self.vin.lower()]:
            response = self.client.get(reverse('dashboard:search'), {'query': value, 'select': 'xelon'})
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/', status_code=302)

    def test_search_xelon_is_valid(self):
        self.client.login(username='toto', password='totopassword')
        for value in ['A123456789', 'a123456789']:
            response = self.client.get(reverse('dashboard:search'), {'query': value, 'select': 'xelon'})
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/', status_code=302)

    def test_config_edit_page_is_not_staff(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('dashboard:config-edit'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/config/edit/', status_code=302)

    def test_config_edit_page_is_staff(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('dashboard:config-edit'))
        self.assertEqual(response.status_code, 200)
