from django.core.management import call_command
from django.test import TestCase

from io import StringIO

from squalaetp.models import ProductCode


class XelonCommandTestCase(TestCase):

    def test_stockparts(self):
        out = StringIO()
        call_command('stockparts', '-f' 'reman/tests/extraction_test.csv', stdout=out)
        self.assertIn(
            "[STOCKPARTS] Data update completed: CSV_LINES = 2 | ADD = 2 | UPDATE = 0 | TOTAL = 2",
            out.getvalue()
        )
        self.assertEqual(ProductCode.objects.count(), 2)

        out = StringIO()
        call_command('stockparts', '--delete', stdout=out)
        self.assertIn(
            "Suppression des données de la table SparePart terminée!",
            out.getvalue(),
        )
        self.assertEqual(ProductCode.objects.count(), 0)
