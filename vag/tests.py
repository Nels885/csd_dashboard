from django.urls import reverse

from dashboard.tests.base import UnitTest


class VagTestCase(UnitTest):

    def setUp(self):
        super(VagTestCase, self).setUp()

    def test_useful_links_page(self):
        response = self.client.get(reverse('vag:useful_links'))
        self.assertEqual(response.status_code, 200)
