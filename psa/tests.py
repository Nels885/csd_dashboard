from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.translation import ugettext as _

from dashboard.tests.base import UnitTest


class PsaTestCase(UnitTest):

    def setUp(self):
        super(PsaTestCase, self).setUp()
        self.psa_url = "https://majestic-web.mpsa.com/mjf00-web/rest/UpdateDownload?uin={}&updateId={}"

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

    def test_useful_links_page(self):
        response = self.client.get(reverse('psa:useful_links'))
        self.assertEqual(response.status_code, 200)
