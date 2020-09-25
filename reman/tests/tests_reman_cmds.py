from django.core.management import call_command
from django.test import TestCase

from io import StringIO

from reman.models import SparePart, EcuRefBase, EcuModel, EcuType


class RemanCommandTestCase(TestCase):

    def test_clearreman(self):
        out = StringIO()
        call_command('clearreman', stdout=out)
        self.assertIn(
            "Suppression des données des tables REMAN terminée!",
            out.getvalue()
        )

    def test_ecurefbase(self):
        out = StringIO()
        call_command('ecurefbase', '-s', 1, '-f', 'reman/tests/Base_réf_ECU_test.xlsx', stdout=out)
        self.assertIn(
            "[ECUREFBASE] Data update completed: CSV_LINES = 5 | ADD = 4 | UPDATE = 1 | TOTAL = 4",
            out.getvalue()
        )
        self.assertIn(
            "[ECUMODEL] Data update completed: CSV_LINES = 5 | ADD = 5 | UPDATE = 0 | TOTAL = 5",
            out.getvalue()
        )
        self.assertEqual(EcuRefBase.objects.count(), 4)
        self.assertEqual(EcuModel.objects.count(), 5)
        self.assertEqual(SparePart.objects.count(), 4)
        self.assertEqual(EcuType.objects.count(), 4)

        out = StringIO()
        call_command('ecurefbase', '--delete', stdout=out)
        self.assertIn(
            "Suppression des données de la table EcuRefBase terminée!",
            out.getvalue()
        )

    def test_spareparts(self):
        out = StringIO()
        call_command('spareparts', '-f', 'reman/tests/extraction_test.csv', stdout=out)
        self.assertIn(
            "[SPAREPARTS] Data update completed: CSV_LINES = 2 | ADD = 2 | UPDATE = 0 | TOTAL = 2",
            out.getvalue()
        )
        self.assertEqual(SparePart.objects.count(), 2)

        out = StringIO()
        SparePart.objects.create(code_produit='test')
        call_command('spareparts', '--delete', stdout=out)
        self.assertIn(
            "Suppression des données de la table SparePart terminée!",
            out.getvalue()
        )
        self.assertEqual(SparePart.objects.count(), 0)
