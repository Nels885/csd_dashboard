from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.translation import ugettext as _

from dashboard.tests.base import UnitTest

from reman.models import Repair, SparePart, Batch, EcuModel, EcuRefBase


class RemanTestCase(UnitTest):

    def setUp(self):
        super().setUp()
        self.redirectUrl = reverse('index')
        self.psaBarcode = '9612345678'
        ref_base = EcuRefBase.objects.create(reman_reference='1234567890')
        ecu = EcuModel.objects.create(oe_raw_reference='1699999999', hw_reference='9876543210', technical_data='test',
                                      ecu_ref_base=ref_base, psa_barcode=self.psaBarcode)
        batch = Batch.objects.create(year="C", number=1, quantity=10, created_by=self.user, ecu_ref_base=ref_base)
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

    def test_check_part(self):
        response = self.client.get(reverse('reman:part_check'))
        self.assertRedirects(response, '/accounts/login/?next=/reman/part/check/', status_code=302)

        self.add_perms_user(EcuModel, 'view_ecumodel')
        self.login()
        response = self.client.get(reverse('reman:part_check'))
        self.assertEqual(response.status_code, 200)

        # Invalid form
        response = self.client.post(reverse('reman:part_check'), {'psa_barcode': ''})
        self.assertFormError(response, 'form', 'psa_barcode', _('This field is required.'))
        for barcode in ['123456789', 'abcdefghij', '96123', '981234567']:
            response = self.client.post(reverse('reman:part_check'), {'psa_barcode': barcode})
            self.assertFormError(response, 'form', 'psa_barcode', _('PSA barcode is invalid'))

        # Valid form
        for barcode in ['9600000000', '9687654321', '9800000000', '9887654321']:
            response = self.client.post(reverse('reman:part_check'), {'psa_barcode': barcode})
            self.assertContains(response, "Le code barre PSA ci-dessous n'éxiste pas dans la base de données REMAN.")
            self.assertContains(response, barcode)
        response = self.client.post(reverse('reman:part_check'), {'psa_barcode': self.psaBarcode})
        ecu = EcuModel.objects.get(psa_barcode=self.psaBarcode)
        self.assertEquals(response.context['ecu'], ecu)

    def test_new_part_email(self):
        response = self.client.get(reverse('reman:part_email', kwargs={'psa_barcode': self.psaBarcode}))
        self.assertRedirects(response, '/accounts/login/?next=/reman/part/9612345678/email/', status_code=302)

        self.add_perms_user(EcuModel, 'view_ecumodel')
        self.login()
        response = self.client.get(reverse('reman:part_email', kwargs={'psa_barcode': self.psaBarcode}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), _('Success: The email has been sent.'))
        self.assertRedirects(response, reverse('reman:part_check'), status_code=302)
