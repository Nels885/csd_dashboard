from django.core.management import call_command
from django.test import TestCase

from io import StringIO


class RaspeediCommandTestCase(TestCase):

    def test_message_of_importraspeedi_commmand_delete(self):
        out = StringIO()
        call_command('importraspeedi', '--delete', stdout=out)
        self.assertIn(
            "Suppression des données de la table Raspeedi terminée!",
            out.getvalue()
        )
