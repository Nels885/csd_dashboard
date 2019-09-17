from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User, Group

from dashboard.models import CsdSoftware
from squalaetp.models import Xelon


class DashboardTestCase(TestCase):

    def setUp(self):
        self.form_data = {
            'jig': 'test', 'new_version': '1', 'link_download': 'test', 'status': 'En test',
        }
        self.vin = 'VF3ABCDEF12345678'
        user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        user.groups.add(Group.objects.create(name="cellule"))
        user.save()
        Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                             modele_vehicule='peugeot')
        self.redirectUrl = reverse('index')

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_set_language_view_is_valid(self):
        for lang in ['fr', 'en']:
            response = self.client.get(reverse('dashboard:set-lang', args={'user_language': lang}),
                                       HTTP_REFERER=self.redirectUrl)
            self.assertTrue(translation.check_for_language(lang))
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.redirectUrl)

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

    def test_search_is_not_found(self):
        response = self.client.get(reverse('dashboard:search'), {'query': 'null', 'select': 'xelon'},
                                   HTTP_REFERER=self.redirectUrl)
        self.assertEqual(response.status_code, 404)

    def test_search_is_not_value(self):
        response = self.client.get(reverse('dashboard:search'), HTTP_REFERER=self.redirectUrl)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.redirectUrl)

    def test_search_vin_is_valid(self):
        response = self.client.get(reverse('dashboard:search'), {'query': self.vin, 'select': 'xelon'})
        self.assertEqual(response.status_code, 200)

    def test_search_xelon_is_valid(self):
        response = self.client.get(reverse('dashboard:search'), {'query': 'A123456789', 'select': 'xelon'})
        self.assertEqual(response.status_code, 200)
