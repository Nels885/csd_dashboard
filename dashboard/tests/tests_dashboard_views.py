import json

from django.utils.translation import ugettext as _
from django.utils import translation

from .base import UnitTest, User, reverse

from dashboard.models import ShowCollapse
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

    def test_charts_page(self):
        response = self.client.get(reverse('dashboard:charts'))
        self.assertEqual(response.status_code, 200)

    def test_charts_ajax(self):
        response = self.client.get(reverse('dashboard:charts_ajax'), format='json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 15)

    def test_late_products(self):
        response = self.client.get(reverse('dashboard:late_prod'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/late-prod/', status_code=302)
        self.login()
        response = self.client.get(reverse('dashboard:late_prod'))
        self.assertEqual(response.status_code, 200)

    def test_set_language_view_is_valid(self):
        for lang in ['fr', 'en']:
            response = self.client.get(reverse('dashboard:set_lang', args={'user_language': lang}),
                                       HTTP_REFERER=self.redirectUrl)
            self.assertTrue(translation.check_for_language(lang))
            self.assertRedirects(response, self.redirectUrl, status_code=302)

    def test_user_profile(self):
        response = self.client.get(reverse('dashboard:user_profile'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/profile/', status_code=302)
        self.login()
        response = self.client.get(reverse('dashboard:user_profile'))
        self.assertEqual(response.status_code, 200)

        # Testing the collapse activation form
        response = self.client.post(
            reverse('dashboard:user_profile'),
            data={
                'user': self.user, 'general': True, 'motor': True, 'interior': True, 'diverse': True,
                'btn_collapse': 'Submit'
            }
        )
        collapse = ShowCollapse.objects.get(user=self.user)
        for field in [collapse.general, collapse.motor, collapse.interior, collapse.diverse]:
            self.assertEqual(field, True)

    def test_signup_page(self):
        # Signug is not staff
        self.login()
        response = self.client.get(reverse('dashboard:signup'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/signup/', status_code=302)

        # Signup is staff
        self.login('admin')
        response = self.client.get(reverse('dashboard:signup'))
        self.assertEqual(response.status_code, 200)

        # Signup is not valid
        old_user = User.objects.count()
        response = self.client.post(reverse('dashboard:signup'), {'username': '', 'email': 'test@test.com'})
        new_user = User.objects.count()
        self.assertEqual(new_user, old_user)
        self.assertFormError(response, 'form', 'username', _('This field is required.'))
        self.assertEqual(response.status_code, 200)

        # Signup is valid
        old_user = User.objects.count()
        response = self.client.post(reverse('dashboard:signup'), self.formUser)
        new_user = User.objects.count()
        self.assertEqual(new_user, old_user + 1)
        self.assertEqual(response.status_code, 200)

        # Signup is user exists
        old_user = User.objects.count()
        response = self.client.post(reverse('dashboard:signup'), {'username': 'toto', 'email': 'test@test.com'})
        new_user = User.objects.count()
        self.assertEqual(new_user, old_user)
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        response = self.client.get('/dashboard/search/?query=null&select=xelon')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/search/%3Fquery%3Dnull%26select%3Dxelon')

        # Search is not found
        self.login()
        for value in ['null', 'A1234567890', 'azertyuiop123456789', 'AZERTIOP']:
            response = self.client.get(reverse('dashboard:search'), {'query': 'null', 'select': 'xelon'},
                                       HTTP_REFERER=self.redirectUrl)
            self.assertRedirects(response, self.redirectUrl, status_code=302)

        # Search is not value
        response = self.client.get(reverse('dashboard:search'), HTTP_REFERER=self.redirectUrl)
        self.assertRedirects(response, self.redirectUrl, status_code=302)

        # Search by VIN is valid
        for value in [self.vin, self.vin.lower()]:
            response = self.client.get(reverse('dashboard:search'), {'query': value, 'select': 'xelon'})
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/', status_code=302)
        Xelon.objects.create(numero_de_dossier='A123456780', vin=self.vin, modele_produit='produit',
                             modele_vehicule='peugeot')
        response = self.client.get(reverse('dashboard:search'), {'query': self.vin, 'select': 'ihm'})
        self.assertEqual(response.status_code, 200)

        # Search by Xelon is valid
        for value in ['A123456789', 'a123456789']:
            response = self.client.get(reverse('dashboard:search'), {'query': value, 'select': 'xelon'})
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/', status_code=302)

    def test_supplier_links_page(self):
        url = reverse('dashboard:supplier_links')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_other_links_page(self):
        url = reverse('dashboard:other_links')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
