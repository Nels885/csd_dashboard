from django.urls import reverse

from dashboard.tests.base import UnitTest


class RemanTestCase(UnitTest):

    def setUp(self):
        super().setUp()
        self.add_group_user("cellule")
        self.redirectUrl = reverse('index')

    def test_reman_table_page(self):
        response = self.client.get(reverse('reman:reman-table'))
        self.assertEqual(response.status_code, 200)

    def test_reman_create_page_is_disconnected(self):
        response = self.client.get(reverse('reman:new-folder'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/reman/add/')

    def test_reman_create_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('reman:new-folder'))
        self.assertEqual(response.status_code, 200)
