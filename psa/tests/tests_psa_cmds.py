from django.core.management import call_command
from io import StringIO

from dashboard.tests.base import UnitTest


class PsaCommandTestCase(UnitTest):

    def setUp(self):
        super(type(self), self).setUp()
        self.out = StringIO()

    def test_clear_psa_multimedia_table(self):
        call_command('clearpsa', '--multimedia', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Multimedia terminée!",
            self.out.getvalue()
        )

    def test_clear_psa_ecu_table(self):
        call_command('clearpsa', '--ecu', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Ecu terminée!",
            self.out.getvalue()
        )
