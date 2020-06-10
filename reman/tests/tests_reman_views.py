from django.urls import reverse

from dashboard.tests.base import UnitTest

from squalaetp.models import Corvet
from reman.models import Repair, SparePart, Batch, EcuModel


class RemanTestCase(UnitTest):

    def setUp(self):
        super().setUp()
        self.redirectUrl = reverse('index')
        ecu = EcuModel.objects.create(es_reference='1234567890', oe_reference='160000000',
                                      oe_raw_reference='1699999999', hw_reference='9876543210', technical_data='test')
        batch = Batch.objects.create(year="C", number=1, quantity=10, created_by=self.user, ecu_model=ecu)
        self.repair = Repair.objects.create(batch=batch, identify_number="C001010001", created_by=self.user)

    def test_repair_table_page(self):
        response = self.client.get(reverse('reman:repair_table'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/repair/table/', status_code=302)

        # Test if connected with permissions
        self.add_perms_user(Repair, 'view_repair')
        self.login()
        response = self.client.get(reverse('reman:repair_table'))
        self.assertEqual(response.status_code, 200)

    def test_spare_part_table_page(self):
        response = self.client.get(reverse('reman:part_table'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/part/table/', status_code=302)

        self.add_perms_user(SparePart, 'view_sparepart')
        self.login()
        response = self.client.get(reverse('reman:part_table'))
        self.assertEqual(response.status_code, 200)

    def test_repair_create_page(self):
        response = self.client.get(reverse('reman:create_repair'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/repair/create/', status_code=302)

        self.add_perms_user(Repair, 'add_repair')
        self.login()
        response = self.client.get(reverse('reman:create_repair'))
        self.assertEqual(response.status_code, 200)

    def test_repair_edit_page(self):
        response = self.client.get(reverse('reman:edit_repair', kwargs={'pk': self.repair.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/reman/repair/' + str(self.repair.pk) + '/edit/',
                             status_code=302)

        self.add_perms_user(Repair, 'change_repair')
        self.login()
        response = self.client.get(reverse('reman:edit_repair', kwargs={'pk': self.repair.pk}))
        self.assertEqual(response.status_code, 200)

    def test_batch_table(self):
        response = self.client.get(reverse('reman:batch_table'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/batch/table/', status_code=302)

        self.add_perms_user(Batch, 'view_batch')
        self.login()
        response = self.client.get(reverse('reman:batch_table'))
        self.assertEqual(response.status_code, 200)

    def test_out_table(self):
        response = self.client.get(reverse('reman:out_table'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/repair/out/table/', status_code=302)

        self.add_perms_user(Repair, 'change_repair')
        self.login()
        response = self.client.get(reverse('reman:out_table'))
        self.assertEqual(response.status_code, 200)
