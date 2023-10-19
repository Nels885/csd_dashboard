import json

from django.utils.translation import gettext as _
from django.utils import translation

from .base import UnitTest, User
from utils.django.urls import reverse

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
        self.assertEqual(len(data), 35)

    def test_send_email_async(self):
        url = reverse('dashboard:email_ajax')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.login("admin")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

    def test_late_products(self):
        url = reverse('dashboard:products', get={'filter': 'late'})
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], _('Late Products'))

    def test_pending_products(self):
        url = reverse('dashboard:products', get={'filter': 'pending'})
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], _('Pending Products'))

    def test_autotronik(self):
        url = reverse('dashboard:products', get={'filter': 'tronik'})
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], 'Autotronik')

    def test_vip_products(self):
        url = reverse('dashboard:vip_prod')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], _('VIP Products'))

    def test_admin_products(self):
        url = reverse('dashboard:admin_prod')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], _('Admin Products'))

    def test_set_language_view_is_valid(self):
        for lang in ['fr', 'en']:
            response = self.client.get(reverse('dashboard:set_lang', args={'user_language': lang}))
            self.assertTrue(translation.check_for_language(lang))
            self.assertRedirects(response, self.redirectUrl, status_code=302)

    def test_user_profile(self):
        url = reverse('dashboard:user_profile')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
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
        url = reverse('dashboard:signup')
        self.login()
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        # Signup is staff
        self.add_perms_user(User, 'add_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Signup is not valid
        old_user = User.objects.count()
        response = self.client.post(url, {'username': '', 'email': 'test@test.com'})
        new_user = User.objects.count()
        self.assertEqual(new_user, old_user)
        self.assertFormError(response, 'form', 'username', _('This field is required.'))
        self.assertEqual(response.status_code, 200)

        # Signup is valid
        old_user = User.objects.count()
        response = self.client.post(url, self.formUser)
        new_user = User.objects.count()
        self.assertEqual(new_user, old_user + 1)
        self.assertEqual(response.status_code, 200)

        # Signup is user exists
        old_user = User.objects.count()
        response = self.client.post(url, {'username': 'toto', 'email': 'test@test.com'})
        new_user = User.objects.count()
        self.assertEqual(new_user, old_user)
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        url = reverse('dashboard:search')
        response = self.client.get(url, {'query': 'null', 'select': 'xelon'})
        self.assertRedirects(response, self.nextLoginUrl + url + '%3Fquery%3Dnull%26select%3Dxelon', status_code=302)

        # Search is not found
        self.login()
        for value in ['null', 'A1234567890', 'azertyuiop123456789', 'AZERTIOP']:
            response = self.client.get(url, {'query': value, 'select': 'xelon'})
            self.assertRedirects(response, self.redirectUrl, status_code=302)

        # Search is not value
        response = self.client.get(url, HTTP_REFERER=self.redirectUrl)
        self.assertRedirects(response, self.redirectUrl, status_code=302)

        # Search by VIN is valid
        for value in [self.vin, self.vin.lower()]:
            response = self.client.get(url, {'query': value, 'select': 'repair'})
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/', status_code=302)
        Xelon.objects.create(numero_de_dossier='A123456780', vin=self.vin, modele_produit='produit',
                             modele_vehicule='peugeot')
        response = self.client.get(url, {'query': self.vin, 'select': 'repair'})
        self.assertRedirects(response, '/squalaetp/xelon/?filter=' + self.vin, status_code=302)
        response = self.client.get(reverse('dashboard:search'), {'query': self.vin, 'select': 'reman'})
        self.assertRedirects(response, self.redirectUrl, status_code=302)

        # Search by Xelon is valid
        for value in ['A123456789', 'a123456789']:
            response = self.client.get(reverse('dashboard:search'), {'query': value, 'select': 'repair'})
            self.assertRedirects(response, '/squalaetp/' + self.xelonId + '/detail/', status_code=302)

    def test_search_ajax(self):
        url = reverse('dashboard:search_ajax')
        # Search is not valid
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {"url": "/dashboard/search/", "task_id": None})
        self.assertEqual(len(data), 2)

        # Search is valid
        params = {'query': 'test', 'select': 'repair'}
        response = self.client.post(url, params )
        data = json.loads(response.content)
        self.assertEqual(data['url'], reverse('dashboard:search', get=params))
        self.assertEqual(len(data), 2)

    def test_activity_log_page(self):
        url = reverse('dashboard:activity_log')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

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
