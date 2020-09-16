from django.core.management import call_command
from django.test import TestCase

from io import StringIO

from squalaetp.models import ProductCode


class XelonCommandTestCase(TestCase):

    def test_message_of_xelon_commmand_delete(self):
        out = StringIO()
        call_command('xelon', '--delete', stdout=out)
        self.assertIn(
            "Suppression des données de la table Xelon terminée!",
            out.getvalue()
        )

    def test_stockparts(self):
        out = StringIO()
        call_command('stockparts', '-f' 'reman/tests/extraction_test.csv', stdout=out)
        self.assertEqual(
            out.getvalue(),
            "\x1b[32;1mSpareParts data update completed: CSV_LINES = 2 | ADD = 2 | UPDATE = 0 | TOTAL = 2\x1b[0m\n"
        )
        self.assertEqual(ProductCode.objects.count(), 2)

        out = StringIO()
        call_command('stockparts', '--delete', stdout=out)
        self.assertEqual(
            out.getvalue(),
            "\x1b[33;1mSuppression des données de la table SparePart terminée!\x1b[0m\n"
        )
        self.assertEqual(ProductCode.objects.count(), 0)
