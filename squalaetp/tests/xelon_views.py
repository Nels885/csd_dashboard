from django.test import TestCase
from django.urls import reverse


class XelonTestCase(TestCase):

    def test_xelon_table_page(self):
        response = self.client.get(reverse('squalaetp:xelon'))
        self.assertEqual(response.status_code, 200)
