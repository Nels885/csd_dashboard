from django.core.management import call_command
from django.test import TestCase

from io import StringIO


class XelonCommandTestCase(TestCase):

    def test_message_of_xelon_commmand_delete(self):
        out = StringIO()
        call_command('xelon', '--delete', stdout=out)
        self.assertIn(
            "Suppression des données de la table Xelon terminée!",
            out.getvalue()
        )
