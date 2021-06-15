from django.utils import timezone
from django.core.management import call_command

from io import StringIO

from dashboard.tests.base import UnitTest
from tools.models import Suptech


class ToolsCommandTestCase(UnitTest):

    def setUp(self):
        super(type(self), self).setUp()
        Suptech.objects.create(
            date=timezone.now(), user='test', xelon='A123456789', item='Hot Line Tech', time='5', info='test',
            rmq='test', created_by=self.user
        )
        self.out = StringIO()

    def test_clear_TagXelon_table(self):
        call_command('cleartools', '--tag_xelon', stdout=self.out)
        self.assertIn("Suppression des données de la table TagXelon terminée!", self.out.getvalue())

    def test_clear_ThermalChamber_table(self):
        call_command('cleartools', '--thermal_chamber', stdout=self.out)
        self.assertIn("Suppression des données de la table ThermalChamber terminée!", self.out.getvalue())

    def test_clear_Suptech_table(self):
        call_command('cleartools', '--suptech', stdout=self.out)
        self.assertIn("Suppression des données de la table Suptech terminée!", self.out.getvalue())

    def test_clear_BgaTime_table(self):
        call_command('cleartools', '--bga_time', stdout=self.out)
        self.assertIn("Suppression des données de la table BgaTime terminée!", self.out.getvalue())

    def test_send_email_suptech(self):
        call_command('suptech', '--email', stdout=self.out)
        self.assertIn("Envoi de l'email des Suptech en cours terminée !", self.out.getvalue())

        # If no Suptech pending or in progress
        Suptech.objects.all().update(status="Cloturée")
        call_command('suptech', '--email', stdout=self.out)
        self.assertIn("Pas de Suptech en cours à envoyer !", self.out.getvalue())
