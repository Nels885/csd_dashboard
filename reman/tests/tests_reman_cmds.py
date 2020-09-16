from django.core.management import call_command
from django.test import TestCase

from io import StringIO

from reman.models import SparePart


class RemanCommandTestCase(TestCase):

    def test_clearreman(self):
        out = StringIO()
        call_command('clearreman', stdout=out)
        self.assertEqual(
            out.getvalue(),
            "\x1b[32;1mSuppression des données des tables REMAN terminée!\x1b[0m\n"
        )

    def test_ecurefbase(self):
        out = StringIO()
        # call_command('ecurefbase', '1', '-f' 'reman/tests/Base_réf_ECU_test.xlsx', stdout=out)
        # self.assertEqual(
        #     out.getvalue(),
        #     "\x1b[32;1mEcuRefBase data update completed: CSV_LINES = 5 | ADD = 4 | UPDATE = 1 | TOTAL = 4\x1b[0m\n" +
        #     "\x1b[32;1mEcuModel data update completed: CSV_LINES = 5 | ADD = 5 | UPDATE = 0 | TOTAL = 5\x1b[0m\n"
        # )
        # self.assertEqual(EcuRefBase.objects.count(), 4)
        # self.assertEqual(EcuModel.objects.count(), 5)
        # self.assertEqual(SparePart.objects.count(), 4)
        # self.assertEqual(EcuType.objects.count(), 4)

        out = StringIO()
        call_command('ecurefbase', '1', '--delete', stdout=out)
        self.assertEqual(
            out.getvalue(),
            "\x1b[33;1mSuppression des données de la table EcuRefBase terminée!\x1b[0m\n"
        )

    def test_spareparts(self):
        # out = StringIO()
        # call_command('spareparts', '-f' 'reman/tests/extraction_test.csv', stdout=out)
        # self.assertEqual(
        #     out.getvalue(),
        #     "\x1b[32;1mSpareParts data update completed: CSV_LINES = 2 | ADD = 2 | UPDATE = 0 | TOTAL = 2\x1b[0m\n"
        # )
        # self.assertEqual(SparePart.objects.count(), 2)

        out = StringIO()
        SparePart.objects.create(code_produit='test')
        call_command('spareparts', '--delete', stdout=out)
        self.assertEqual(
            out.getvalue(),
            "\x1b[33;1mSuppression des données de la table SparePart terminée!\x1b[0m\n"
        )
        self.assertEqual(SparePart.objects.count(), 0)
