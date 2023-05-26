from django.core.management import call_command

from io import StringIO

from dashboard.tests.base import UnitTest
from tools.models import Suptech, SuptechCategory


class ToolsCommandTestCase(UnitTest):

    def setUp(self):
        super(type(self), self).setUp()
        for name in ['Cellule Operation', 'Cellule Etude', 'Modif. process']:
            SuptechCategory.objects.create(name=name, manager=self.user)
        Suptech.objects.create(
            date="1970-01-01", user='test', xelon='A123456789', item='Hot Line Tech', time='5', info='test',
            rmq='test', created_by=self.user, category=SuptechCategory.objects.first()
        )
        self.out = StringIO()

    def test_clear_TagXelon_table(self):
        call_command('cleartools', '--tag_xelon', stdout=self.out)
        self.assertIn("Suppression des données de la table TagXelon terminée!", self.out.getvalue())

    def test_clear_ThermalChamber_table(self):
        call_command('cleartools', '--thermal_chamber', stdout=self.out)
        self.assertIn("Suppression des données de la table ThermalChamber terminée!", self.out.getvalue())

    def test_clear_ThermalChamberMeasure_table(self):
        call_command('cleartools', '--thermal_chamber_measure', stdout=self.out)
        self.assertIn("Suppression des données de la table ThermalChamberMeasure terminée!", self.out.getvalue())

    def test_clear_Suptech_table(self):
        call_command('cleartools', '--suptech', stdout=self.out)
        self.assertIn("Suppression des données de la table Suptech terminée!", self.out.getvalue())

    def test_clear_BgaTime_table(self):
        call_command('cleartools', '--bga_time', stdout=self.out)
        self.assertIn("Suppression des données de la table BgaTime terminée!", self.out.getvalue())

    def test_send_email_suptech(self):
        call_command('suptech', '--email', stdout=self.out)
        self.assertIn("Envoi de l'email des Suptech en cours terminée !", self.out.getvalue())

        # If Suptech 48h pending or in progress
        call_command('suptech', '--email_48h', stdout=self.out)
        self.assertIn("Envoi de l'email Suptech n°", self.out.getvalue())

        # If Suptech 48 late
        call_command('suptech', '--email_48h_late', stdout=self.out)
        self.assertIn("Envoi de l'email des Suptech en retard terminée !", self.out.getvalue())

        # If no Suptech pending or in progress
        Suptech.objects.all().update(status="Cloturée")
        call_command('suptech', '--email', stdout=self.out)
        self.assertIn("Pas de Suptech en cours à envoyer !", self.out.getvalue())

        # If no Suptech 48h pending or in progress
        call_command('suptech', '--email_48h', stdout=self.out)

        # If no Suptech 48 late
        call_command('suptech', '--email_48h_late', stdout=self.out)
        self.assertIn("Pas de Suptech en retard à envoyer !", self.out.getvalue())

    def test_suptech_product_update(self):
        call_command('suptech', '--prod_update', stdout=self.out)
        self.assertIn("[SUPTECH] Update xelon product completed.", self.out.getvalue())
