from django.core.management import call_command
from django.test import TestCase

from io import StringIO


class RaspeediCommandTestCase(TestCase):

    def setUp(self):
        super(type(self), self).setUp()
        self.out = StringIO()

    def test_clear_raspeedi_table(self):
        call_command('loadraspeedi', '--delete', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Raspeedi terminée!",
            self.out.getvalue()
        )

    def test_clear_programing_table(self):
        call_command('programing', '--delete', stdout=self.out)
        self.assertIn(
            "Suppression des données des tables Raspeedi terminée!",
            self.out.getvalue()
        )
