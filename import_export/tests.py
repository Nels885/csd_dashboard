import csv
import io
from django.urls import reverse

from dashboard.tests.base import UnitTest
from squalaetp.models import Corvet
from reman.models import Batch, Repair, SparePart, EcuModel


class ImportExportTestCase(UnitTest):

    def setUp(self):
        super(ImportExportTestCase, self).setUp()
        self.add_perms_user(EcuModel, 'add_ecumodel', 'change_ecumodel')
        Corvet.objects.create(vin=self.vin, electronique_14x='9812345680')

    def export_csv(self, name):
        return self.client.get(reverse('import_export:export_{}_csv'.format(name)))

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
        self.assertRedirects(response, '/import-export/detail/', status_code=302)
