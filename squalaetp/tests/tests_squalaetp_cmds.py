from django.core.management import call_command
from django.test import TestCase

from io import StringIO

from squalaetp.models import ProductCode


class XelonCommandTestCase(TestCase):

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
