import csv
import io
from django.urls import reverse

from dashboard.tests.base import UnitTest
from squalaetp.models import Corvet
from reman.models import Batch, Repair, SparePart


class ImportExportTestCase(UnitTest):

    def setUp(self):
        super(ImportExportTestCase, self).setUp()
        self.add_perms_user(Corvet, 'change_corvet', 'add_corvet')
        self.add_perms_user(Batch, 'view_batch')
        self.add_perms_user(Repair, 'view_repair')

    def export_csv(self, name):
        return self.client.get(reverse('import_export:export_{}_csv'.format(name)))

    def test_export_corvet_csv(self):
        self.login()
        response = self.client.post(reverse('squalaetp:corvet_insert'), {'vin': self.vin, 'xml_data': self.xmlData})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('import_export:export_corvet_csv'))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        headers = body.pop(0)
        self.assertEqual(len(body), 1)
        self.assertEqual(len(headers), 1)

    def test_export_product_csv(self):
        self.login()
        for prod in ['bsi', 'ecu', 'com']:
            response = self.export_csv(prod)
            self.assertEqual(response.status_code, 200)

            content = response.content.decode('utf-8')
            csv_reader = csv.reader(io.StringIO(content))
            body = list(csv_reader)
            headers = body.pop(0)
            self.assertEqual(len(body), 0)
            self.assertEqual(len(headers), 1)

    def test_export_reman_csv(self):
        self.login()
        for table in ['batch', 'repair']:
            response = self.export_csv(table)
            self.assertEqual(response.status_code, 200)

            content = response.content.decode('utf-8')
            csv_reader = csv.reader(io.StringIO(content))
            body = list(csv_reader)
            headers = body.pop(0)
            self.assertEqual(len(body), 0)
            self.assertEqual(len(headers), 1)

    def test_import_part(self):
        self.add_perms_user(SparePart, 'add_sparepart', 'change_sparepart')
        self.login()
        response = self.client.get(reverse('import_export:import_part'))
        self.assertRedirects(response, '/reman/import-export/', status_code=302)
