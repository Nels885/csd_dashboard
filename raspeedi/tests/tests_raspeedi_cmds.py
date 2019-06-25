from django.core.management import call_command
from django.test import TestCase

from io import StringIO


class RaspeediCommandTestCase(TestCase):

    def test_message_of_raspeedi_commmand_delete(self):
        out = StringIO()
        call_command('raspeedi', '--delete', stdout=out)
        self.assertEqual(
            out.getvalue(),
            "Suppression des données de la table Raspeedi terminée!\n"
        )
