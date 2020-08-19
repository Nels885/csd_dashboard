from django.urls import reverse

from dashboard.tests.base import UnitTest


class PsaTestCase(UnitTest):

    def setUp(self):
        super(PsaTestCase, self).setUp()

    def test_nac_tools_page(self):
        response = self.client.get(reverse('psa:nac_tools'))
        self.assertEqual(response.status_code, 200)

    def test_nac_license(self):
        response = self.client.get(reverse('psa:nac_license'))
        self.assertRedirects(response, reverse('psa:nac_tools'), status_code=302)

    def test_nac_update(self):
        response = self.client.get(reverse('psa:nac_update'))
        self.assertRedirects(response, reverse('psa:nac_tools'), status_code=302)
