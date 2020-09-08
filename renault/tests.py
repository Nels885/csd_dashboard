from django.urls import reverse

from dashboard.tests.base import UnitTest


class RenaultTestCase(UnitTest):

    def setUp(self):
        super(RenaultTestCase, self).setUp()

    def test_useful_links_page(self):
        response = self.client.get(reverse('renault:useful_links'))
        self.assertEqual(response.status_code, 200)
