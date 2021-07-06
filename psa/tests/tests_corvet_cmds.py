from django.core.management import call_command
from django.test import TestCase

from io import StringIO

from psa.models import Corvet


class CorvetCommandTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.out = StringIO()

    def test_message_of_corvet_commmand_delete(self):
        call_command('corvet', '-f' 'dashboard/tests/files/squalaetp_test.xls', stdout=self.out)
        self.assertIn(
            "[CORVET] data update completed: EXCEL_LINES = 2 | ADD = 2 | UPDATE = 0 | TOTAL = 2",
            self.out.getvalue()
        )
        self.assertEqual(Corvet.objects.count(), 2)

        # Test for files not found
        call_command('corvet', '-f' 'test.xls', stdout=self.out)
        self.assertIn("[CORVET] No squalaetp file found", self.out.getvalue())

        call_command('corvet', '--delete', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Corvet terminée!",
            self.out.getvalue()
        )
