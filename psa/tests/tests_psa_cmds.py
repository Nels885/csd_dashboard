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

    def test_clear_psa_corvet_table(self):
        call_command('clearpsa', '--corvet', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Corvet terminée!",
            self.out.getvalue()
        )

    def test_clear_psa_corvet_attribute_table(self):
        call_command('clearpsa', '--corvet_attribute', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table CorvetAttribute terminée!",
            self.out.getvalue()
        )

    def test_cmd_loadsqualaetp(self):
        # Test for files not found
        call_command('loadcorvet', '-f' 'test.xls', stdout=self.out)
        self.assertIn("[CORVET_CMD] No squalaetp file found", self.out.getvalue())

        call_command('loadcorvet', '--import_csv', stdout=self.out)
        self.assertIn("[CORVET_CMD] Missing CSV file", self.out.getvalue())

        call_command('loadcorvet', '--import_csv', '-f', 'test.xls', stdout=self.out)
        self.assertIn("[CORVET_CMD] No CSV file found", self.out.getvalue())

        call_command('loadcorvet', '--attribute', '-f', 'test.xls', stdout=self.out)
        self.assertIn("[CORVET_CMD] No Attribute file found", self.out.getvalue())

        # Test of relationship into Corvet and CorvetProduct
        call_command('loadcorvet', '--relations', stdout=self.out)
        self.assertIn("[CORVET_CMD] Relationships update completed:", self.out.getvalue())
