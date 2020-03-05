from django.urls import reverse

from dashboard.tests.base import UnitTest

from reman.models import Repair, SparePart


class RemanTestCase(UnitTest):

    def setUp(self):
        super().setUp()
        self.redirectUrl = reverse('index')
        self.add_perms_user(Repair, 'add_repair', 'view_repair')
        self.add_perms_user(SparePart, 'add_sparepart', 'view_sparepart')

    def test_repair_table_page_is_disconnected(self):
        response = self.client.get(reverse('reman:repair_table'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/repair/table/', status_code=302)

    def test_repair_table_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('reman:repair_table'))
        self.assertEqual(response.status_code, 200)

    def test_part_table_page_is_disconnected(self):
        response = self.client.get(reverse('reman:part_table'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/part/table/', status_code=302)

    def test_part_table_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('reman:part_table'))
        self.assertEqual(response.status_code, 200)

    def test_repair_create_page_is_disconnected(self):
        response = self.client.get(reverse('reman:new_folder'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/repair/add/', status_code=302)

    def test_repair_create_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('reman:new_folder'))
        self.assertEqual(response.status_code, 200)
