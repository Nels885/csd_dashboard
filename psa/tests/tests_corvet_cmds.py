from django.core.management import call_command
from django.test import TestCase

from io import StringIO


class CorvetCommandTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.out = StringIO()

    def test_message_of_corvet_commmand(self):
        # Test for files not found
        call_command('corvet', '-f' 'test.xls', stdout=self.out)
        self.assertIn("[CORVET] No squalaetp file found", self.out.getvalue())

        call_command('corvet', '--delete', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Corvet terminée!",
            self.out.getvalue()
        )
