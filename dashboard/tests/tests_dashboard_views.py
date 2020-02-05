from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User, Group

from squalaetp.models import Xelon


class DashboardTestCase(TestCase):

    def setUp(self):
        self.vin = 'VF3ABCDEF12345678'
        user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        user.groups.add(Group.objects.create(name="cellule"))
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
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.redirectUrl)

    def test_user_profile_is_disconnected(self):
        response = self.client.get(reverse('dashboard:user-profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/profile/')

    def test_user_profile_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('dashboard:user-profile'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_is_not_staff(self):
        response = self.client.get(reverse('dashboard:register'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/register/')

    def test_search_is_not_found(self):
        for value in ['null', 'A1234567890', 'azertyuiop123456789', 'AZERTIOP']:
            response = self.client.get(reverse('dashboard:search'), {'query': 'null', 'select': 'xelon'},
                                       HTTP_REFERER=self.redirectUrl)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.redirectUrl)

    def test_search_is_not_value(self):
        response = self.client.get(reverse('dashboard:search'), HTTP_REFERER=self.redirectUrl)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.redirectUrl)

    def test_search_vin_is_valid(self):
        for value in [self.vin, self.vin.lower()]:
            response = self.client.get(reverse('dashboard:search'), {'query': self.vin, 'select': 'xelon'})
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/')

    def test_search_xelon_is_valid(self):
        for value in ['A123456789', 'a123456789', 'Z000000000', 'z000000000']:
            response = self.client.get(reverse('dashboard:search'), {'query': 'A123456789', 'select': 'xelon'})
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/')
