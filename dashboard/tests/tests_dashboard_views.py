from django.utils.translation import ugettext as _
from django.utils import translation

from .base import UnitTest, User, reverse

from squalaetp.models import Xelon


class DashboardTestCase(UnitTest):

    def setUp(self):
        super(DashboardTestCase, self).setUp()
        xelon = Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                                     modele_vehicule='peugeot')
        self.xelonId = str(xelon.id)

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_set_language_view_is_valid(self):
        for lang in ['fr', 'en']:
            response = self.client.get(reverse('dashboard:set_lang', args={'user_language': lang}),
                                       HTTP_REFERER=self.redirectUrl)
            self.assertTrue(translation.check_for_language(lang))
            self.assertRedirects(response, self.redirectUrl, status_code=302)

    def test_user_profile_is_disconnected(self):
        response = self.client.get(reverse('dashboard:user_profile'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/profile/', status_code=302)

    def test_user_profile_is_connected(self):
        self.login()
        response = self.client.get(reverse('dashboard:user_profile'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_is_not_staff(self):
        self.login()
        response = self.client.get(reverse('dashboard:signup'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/signup/', status_code=302)

    def test_signup_page_is_staff(self):
        self.login('admin')
        response = self.client.get(reverse('dashboard:signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_is_not_valid(self):
        self.login('admin')
        old_user = User.objects.count()
        response = self.client.post(reverse('dashboard:signup'))
        new_user = User.objects.count()
        self.assertEqual(new_user, old_user)
        self.assertFormError(response, 'form', 'username', _('This field is required.'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_is_valid(self):
        self.login('admin')
        old_user = User.objects.count()
        response = self.client.post(reverse('dashboard:signup'), self.form_user)
        new_user = User.objects.count()
        self.assertEqual(new_user, old_user + 1)
        self.assertEqual(response.status_code, 200)

    def test_signup_page_is_user_exists(self):
        self.login('admin')
        old_user = User.objects.count()
        response = self.client.post(reverse('dashboard:signup'), {'username': 'toto', 'email': 'totopassword'})
        new_user = User.objects.count()
        self.assertEqual(new_user, old_user)
        self.assertEqual(response.status_code, 200)

    def test_search_is_disconnected(self):
        response = self.client.get('/dashboard/search/?query=null&select=xelon')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/search/%3Fquery%3Dnull%26select%3Dxelon')

    def test_search_is_not_found(self):
        self.login()
        for value in ['null', 'A1234567890', 'azertyuiop123456789', 'AZERTIOP']:
            response = self.client.get(reverse('dashboard:search'), {'query': 'null', 'select': 'xelon'},
                                       HTTP_REFERER=self.redirectUrl)
            self.assertRedirects(response, self.redirectUrl, status_code=302)

    def test_search_is_not_value(self):
        self.login()
        response = self.client.get(reverse('dashboard:search'), HTTP_REFERER=self.redirectUrl)
        self.assertRedirects(response, self.redirectUrl, status_code=302)

    def test_search_vin_is_valid(self):
        self.login()
        for value in [self.vin, self.vin.lower()]:
            response = self.client.get(reverse('dashboard:search'), {'query': value, 'select': 'xelon'})
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/', status_code=302)

    def test_search_xelon_is_valid(self):
        self.login()
        for value in ['A123456789', 'a123456789']:
            response = self.client.get(reverse('dashboard:search'), {'query': value, 'select': 'xelon'})
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/', status_code=302)

    def test_config_edit_page_is_not_staff(self):
        self.login()
        response = self.client.get(reverse('dashboard:config_edit'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/config/edit/', status_code=302)

    def test_config_edit_page_is_staff(self):
        self.login('admin')
        response = self.client.get(reverse('dashboard:config_edit'))
        self.assertEqual(response.status_code, 200)
