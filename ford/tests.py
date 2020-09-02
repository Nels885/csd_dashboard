from django.urls import reverse

from dashboard.tests.base import UnitTest


class FordTestCase(UnitTest):

    def setUp(self):
        super(FordTestCase, self).setUp()

    def test_useful_links_page(self):
        response = self.client.get(reverse('ford:useful_links'))
        self.assertEqual(response.status_code, 200)

    def test_tools_page(self):
        response = self.client.get(reverse('ford:tools'))
        self.assertEqual(response.status_code, 200)
