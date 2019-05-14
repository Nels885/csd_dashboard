from django.test import TestCase
from django.urls import reverse


class DashboardTestCase(TestCase):

    def test_raspeedi_table_page(self):
        response = self.client.get(reverse('raspeedi:table'))
        self.assertEqual(response.status_code, 200)
