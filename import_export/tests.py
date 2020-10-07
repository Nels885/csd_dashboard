import csv
import io
from django.urls import reverse

from dashboard.tests.base import UnitTest
from squalaetp.models import Corvet
from reman.models import Repair, SparePart, Batch, EcuModel, EcuRefBase, EcuType


class ImportExportTestCase(UnitTest):

    def setUp(self):
        super(ImportExportTestCase, self).setUp()
        self.add_perms_user(EcuModel, 'add_ecumodel', 'change_ecumodel')
        Corvet.objects.create(vin=self.vin, electronique_14x='9812345680')
        psaBarcode = '9612345678'
        spare_part = SparePart.objects.create(code_produit='test HW_9876543210')
        ecu_type = EcuType.objects.create(hw_reference='9876543210', technical_data='test', spare_part=spare_part)
        ref_base = EcuRefBase.objects.create(reman_reference='1234567890', ecu_type=ecu_type)
        ecu = EcuModel.objects.create(oe_raw_reference='1699999999', ecu_type=ecu_type, psa_barcode=psaBarcode)
        batch = Batch.objects.create(year="C", number=1, quantity=10, created_by=self.user, ecu_ref_base=ref_base)
        Repair.objects.create(batch=batch, identify_number="C001010001", created_by=self.user)

    def test_import_export_page(self):
        url = reverse('import_export:detail')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_export_corvet(self):
        self.add_perms_user(Corvet, 'view_corvet')
        self.login()
        response = self.client.post(reverse('import_export:corvet'),
                                    {'formats': 'csv', 'products': 'corvet', 'btn_corvet_all': ''})
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        headers = body.pop(0)
        self.assertEqual(len(body), 1)
        self.assertEqual(len(headers), 1)

    def test_export_reman_csv(self):
        self.add_perms_user(Batch, 'view_batch')
        self.add_perms_user(Repair, 'view_repair')
        self.add_perms_user(EcuModel, 'view_ecumodel')
        self.login()

        response = self.client.post(reverse('import_export:reman'), {'formats': 'csv', 'tables': 'batch'})
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        headers = body.pop(0)
        self.assertEqual(len(body), 1)
        self.assertEqual(len(headers), 1)

    def test_import_part(self):
        self.add_perms_user(SparePart, 'add_sparepart', 'change_sparepart')
        self.login()
        response = self.client.get(reverse('import_export:import_part'))
        self.assertRedirects(response, '/import-export/detail/', status_code=302)
