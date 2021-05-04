import csv
import io
from django.urls import reverse
from django.utils import timezone

from dashboard.tests.base import UnitTest
from squalaetp.models import Xelon
from psa.models import Corvet
from reman.models import Repair, SparePart, Batch, EcuModel, EcuRefBase, EcuType
from tools.models import Suptech


class ImportExportTestCase(UnitTest):

    def setUp(self):
        super(ImportExportTestCase, self).setUp()
        self.add_perms_user(EcuModel, 'add_ecumodel', 'change_ecumodel')
        corvet = Corvet.objects.create(
            vin=self.vin, electronique_14x='9812345680', electronique_14a='9812345680', electronique_14b='9812345680',
            electronique_16p='9812345680', electronique_16b='9812345680'
        )
        Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, corvet=corvet)
        psaBarcode = '9612345678'
        spare_part = SparePart.objects.create(code_produit='test HW_9876543210')
        ecu_type = EcuType.objects.create(hw_reference='9876543210', technical_data='test', spare_part=spare_part)
        ref_base = EcuRefBase.objects.create(reman_reference='1234567890', ecu_type=ecu_type)
        ecu = EcuModel.objects.create(oe_raw_reference='1699999999', ecu_type=ecu_type, psa_barcode=psaBarcode)
        batch = Batch.objects.create(year="C", number=1, quantity=10, created_by=self.user, ecu_ref_base=ref_base)
        Repair.objects.create(batch=batch, identify_number="C001010001", created_by=self.user)
        Suptech.objects.create(
            date=timezone.now(), user='test', xelon='A123456789', item='Hot Line Tech', time='5', info='test',
            rmq='test', created_by=self.user
        )

    def _http_content(self, response):
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        headers = body.pop(0)
        self.assertEqual(len(body), 1)
        self.assertEqual(len(headers), 1)

    def test_import_export_page(self):
        url = reverse('import_export:detail')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_export_corvet_task(self):
        url = reverse('import_export:export_corvet')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_esport_corvet_vin_task(self):
        url = reverse('import_export:export_corvet_vin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_esport_reman_task(self):
        url = reverse('import_export:export_reman')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_esport_tools_task(self):
        url = reverse('import_export:export_tools')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # def test_export_tools_page(self):
    #     url = reverse('import_export:tools')
    #     response = self.client.post(url, {'formats': 'csv', 'tables': 'suptech'})
    #     self.assertEqual(response.status_code, 302)
    #
    #     self.add_perms_user(Suptech, 'view_suptech')
    #     self.login()
    #
    #     for table in ['suptech']:
    #         response = self.client.post(url, {'formats': 'csv', 'tables': table})
    #         self.assertEqual(response.status_code, 200)
    #         self._http_content(response)

    def test_import_part(self):
        self.add_perms_user(SparePart, 'add_sparepart', 'change_sparepart')
        self.login()
        response = self.client.get(reverse('import_export:import_part'))
        self.assertRedirects(response, '/import-export/detail/', status_code=302)
