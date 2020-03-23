from django.urls import reverse

from dashboard.tests.base import UnitTest

from reman.models import Repair, SparePart, Batch, EcuModel


class RemanTestCase(UnitTest):

    def setUp(self):
        super().setUp()
        self.redirectUrl = reverse('index')
        self.add_perms_user(Repair, 'add_repair', 'view_repair', 'change_repair')
        self.add_perms_user(SparePart, 'add_sparepart', 'view_sparepart')
        ecu = EcuModel.objects.create(es_reference='1234567890', oe_reference='160000000',
                                      oe_raw_reference='1699999999', technical_data='test')
        batch = Batch.objects.create(number=1, quantity=10, created_by=self.user, ecu_model=ecu)
        self.repair = Repair.objects.create(batch=batch, created_by=self.user)

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
        response = self.client.get(reverse('reman:create_repair'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/repair/create/', status_code=302)

    def test_repair_create_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('reman:create_repair'))
        self.assertEqual(response.status_code, 200)

    def test_repair_edit_page_is_disconnected(self):
        response = self.client.get(reverse('reman:edit_repair', kwargs={'pk': self.repair.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/reman/repair/' + str(self.repair.pk) + '/edit/',
                             status_code=302)

    def test_repair_edit_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('reman:edit_repair', kwargs={'pk': self.repair.pk}))
        self.assertEqual(response.status_code, 200)
