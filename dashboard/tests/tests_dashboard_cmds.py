from django.core.management import call_command
from django.test import TestCase

from io import StringIO


class DashboardCommandTestCase(TestCase):

    def test_clear_Group_table(self):
        out = StringIO()
        call_command('clearauth', '--group', stdout=out)
        self.assertIn(
            "Suppression des données de la table Group terminée!",
            out.getvalue()
        )

    def test_clear_Permission_table(self):
        out = StringIO()
        call_command('clearauth', '--permission', stdout=out)
        self.assertIn(
            "Suppression des données de la table Permission terminée!",
            out.getvalue()
        )
