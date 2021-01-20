from django.core.management import call_command
from django.test import TestCase

from io import StringIO


class RemanCommandTestCase(TestCase):

    def test_clear_TagXelon_table(self):
        out = StringIO()
        call_command('cleartools', '--tag_xelon', stdout=out)
        self.assertIn(
            "Suppression des données de la table TagXelon terminée!",
            out.getvalue()
        )

    def test_clear_ThermalChamber_table(self):
        out = StringIO()
        call_command('cleartools', '--thermal_chamber', stdout=out)
        self.assertIn(
            "Suppression des données de la table ThermalChamber terminée!",
            out.getvalue()
        )
