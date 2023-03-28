from django.urls import reverse

from dashboard.tests.base import UnitTest


class RenaultTestCase(UnitTest):

    def setUp(self):
        super(RenaultTestCase, self).setUp()

    def test_useful_links_page(self):
        response = self.client.get(reverse('renault:useful_links'))
        self.assertEqual(response.status_code, 200)

    def test_tool_page(self):
        response = self.client.get(reverse('renault:tools'))
        self.assertEqual(response.status_code, 200)

    def test_ajax_decode(self):
        response = self.client.get(reverse('renault:ajax_decode'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content, {'result': 'ERROR', 'message': 'Could not compute the code with a empty precode !'})
