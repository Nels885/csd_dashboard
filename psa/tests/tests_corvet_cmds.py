from django.core.management import call_command
from django.test import TestCase

from io import StringIO


class CorvetCommandTestCase(TestCase):

    def test_message_of_corvet_commmand_delete(self):
        out = StringIO()
        call_command('corvet', '--delete', stdout=out)
        self.assertIn(
            "Suppression des données de la table Corvet terminée!",
            out.getvalue()
        )
