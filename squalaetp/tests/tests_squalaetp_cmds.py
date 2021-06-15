from django.core.management import call_command
from constance import config
from io import StringIO

from dashboard.tests.base import UnitTest
from squalaetp.models import ProductCode
from utils.conf import string_to_list


class XelonCommandTestCase(UnitTest):

    def setUp(self):
        super(type(self), self).setUp()
        self.out = StringIO()

    def test_loadsparepart_cmd(self):
        out = StringIO()
        call_command('loadsparepart', '-f' 'reman/tests/extraction_test.csv', stdout=out)
        self.assertIn(
            "[SPAREPART] Data update completed: CSV_LINES = 2 | ADD = 2 | UPDATE = 0 | TOTAL = 2",
            out.getvalue()
        )
        self.assertEqual(ProductCode.objects.count(), 2)

        out = StringIO()
        call_command('loadsparepart', '--delete', stdout=out)
        self.assertIn(
            "Suppression des données de la table SparePart terminée!",
            out.getvalue(),
        )
        self.assertEqual(ProductCode.objects.count(), 0)

    def test_loadsqualaetp_cmd(self):
        out = StringIO()

        # Test for files not found
        call_command('loadsqualaetp', '--xelon_update', '-S', 'test.xls', '-D' 'test.xls, test.xls', stdout=out)
        self.assertIn("[XELON] No squalaetp file found", out.getvalue())
        self.assertIn("[DELAY] No delay files found", out.getvalue())

    def test_importcorvet_cmd(self):
        out = StringIO()
        call_command('importcorvet', '--squalaetp', stdout=out)
        self.assertIn("[IMPORT_CORVET] Import completed:", out.getvalue())

    def test_clear_squalaetp_xelon_table(self):
        call_command('clearsqualaetp', '--xelon', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Xelon terminée!",
            self.out.getvalue()
        )

    def test_clear_squalaetp_indicator_table(self):
        call_command('clearsqualaetp', '--indicator', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Indicator terminée!",
            self.out.getvalue()
        )

    def test_clear_squalaetp_product_category_table(self):
        call_command('clearsqualaetp', '--prod_category', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table ProductCategory terminée!",
            self.out.getvalue()
        )

    def test_clear_sparepart_table(self):
        call_command('loadsparepart', '--delete', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table SparePart terminée!",
            self.out.getvalue()
        )

    def test_export_squalaetp_files(self):
        call_command('exportsqualaetp', '--corvet', stdout=self.out)
        self.assertIn("[CORVET_EXPORT] Export completed", self.out.getvalue())
        self.assertIn("squalaetp_corvet.csv", self.out.getvalue())

        call_command('exportsqualaetp', stdout=self.out)
        self.assertIn("[SQUALAETP_EXPORT]", self.out.getvalue())
        for filename in string_to_list(config.SQUALAETP_FILE_LIST):
            self.assertIn(filename, self.out.getvalue())
