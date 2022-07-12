import json

from django.contrib.messages import get_messages
from django.utils.translation import gettext as _

from dashboard.tests.base import UnitTest

from utils.django.urls import reverse
from psa.models import Corvet, Multimedia


class PsaTestCase(UnitTest):

    def setUp(self):
        super(PsaTestCase, self).setUp()
        Corvet.objects.create(vin=self.vin, donnee_marque_commerciale="OP", electronique_14x="1234567890",
                              electronique_94x="1234567890")
        self.psa_url = "https://majestic-web.mpsa.com/mjf00-web/rest/UpdateDownload?uin={}&updateId={}"
        self.authError = {"detail": "Informations d'authentification non fournies."}

    def test_nac_tools_page(self):
        response = self.client.get(reverse('psa:nac_tools'))
        self.assertEqual(response.status_code, 200)

    def test_nac_license(self):
        url = reverse('psa:nac_license')
        psa_url = self.psa_url + "&type=license"
        response = self.client.get(url)
        self.assertRedirects(response, reverse('psa:nac_tools'), status_code=302)

        # Form is not valid
        response = self.client.post(url, {'software': '', 'uin': ''})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertIn(_('This field is required.'), str(messages[0]))

        # Form is valid
        response = self.client.post(url, {'software': '001315031548167166', 'uin': '0D01172241D4EA123456'})
        self.assertEqual(response.status_code, 302)

    def test_nac_update_id_license(self):
        url = reverse('psa:nac_id_license')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('psa:nac_tools'), status_code=302)

        # From is not valid
        response = self.client.post(url, {'uin': '', 'update': ''})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertIn(_('This field is required.'), str(messages[0]))

    def test_nac_update(self):
        url = reverse('psa:nac_update')
        psa_url = self.psa_url + "&type=update"
        response = self.client.get(url)
        self.assertRedirects(response, reverse('psa:nac_tools'), status_code=302)

        response = self.client.post(url, {'software': ''})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(_('This field is required.'), str(messages[0]))

        # Form is valid
        response = self.client.post(url, {'software': '001315031548167166'})
        self.assertEqual(response.status_code, 302)

    def test_majestic_web(self):
        url = reverse('psa:majestic_web')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('index'), status_code=302)

    def test_useful_links_page(self):
        response = self.client.get(reverse('psa:useful_links'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_table_page(self):
        response = self.client.get(reverse('psa:corvet'))
        self.assertEqual(response.status_code, 302)
        self.add_perms_user(Corvet, 'view_corvet')
        self.login()
        response = self.client.get(reverse('psa:corvet'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_detail_page(self):
        url = reverse('psa:corvet_detail', kwargs={'vin': self.vin})

        # Detail page is disconnected
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(Corvet, 'view_corvet')
        self.login()

        # Detail is not found
        response = self.client.get(reverse('psa:corvet_detail', kwargs={'vin': "123456789"}))
        self.assertEqual(response.status_code, 404)

        # Detail is found
        response = self.client.get(reverse('psa:corvet_detail', kwargs={'vin': self.vin}))
        self.assertEqual(response.status_code, 200)

    def test_corvet_view_set_is_disconnected(self):
        response = self.client.get(reverse('psa:api_corvet-list'), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.authError)

    def test_product_table_page(self):
        response = self.client.get(reverse('psa:product'))
        self.assertEqual(response.status_code, 302)
        self.add_perms_user(Multimedia, 'view_multimedia')
        self.login()
        response = self.client.get(reverse('psa:product'))
        self.assertEqual(response.status_code, 200)

    def test_import_corvet_async(self):
        response = self.client.get(reverse('psa:import_corvet'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertDictEqual(data, {"nothing to see": "this isn't happening"})

        # request is valid
        response = self.client.get(reverse('psa:import_corvet', get={'vin': self.vin}))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertNotEqual(data.get('task_id', None), None)
