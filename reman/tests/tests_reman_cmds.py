import os
from django.core.management import call_command

from dashboard.tests.base import UnitTest

from io import StringIO

from utils.conf import CSD_ROOT, conf
from reman.models import EcuRefBase, EcuModel, EcuType


class RemanCommandTestCase(UnitTest):

    def setUp(self):
        super(type(self), self).setUp()
        self.out = StringIO()

    def test_clear_reman_batch_table(self):
        call_command('clearreman', '--batch', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Batch terminée!",
            self.out.getvalue()
        )

    def test_clear_reman_default_table(self):
        call_command('clearreman', '--default', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Default terminée!",
            self.out.getvalue()
        )

    def test_clear_reman_ecumodel_table(self):
        call_command('clearreman', '--ecumodel', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table EcuModel terminée!",
            self.out.getvalue()
        )

    def test_clear_reman_ecutype_table(self):
        call_command('clearreman', '--ecutype', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table EcuType terminée!",
            self.out.getvalue()
        )

    def test_clear_reman_all_table(self):
        call_command('clearreman', '--all', stdout=self.out)
        self.assertIn(
            "Suppression des données des tables REMAN terminée!",
            self.out.getvalue()
        )

    def test_ecurefbase(self):
        call_command('ecurefbase', '-s', 1, '-f', 'reman/tests/Base_réf_ECU_test.xlsx', stdout=self.out)
        self.assertIn(
            "[ECUREFBASE] Data update completed: EXCEL_LINES = 5 | ADD = 4 | UPDATE = 1 | TOTAL = 4",
            self.out.getvalue()
        )
        self.assertIn(
            "[ECUMODEL] Data update completed: EXCEL_LINES = 5 | ADD = 5 | UPDATE = 0 | TOTAL = 5",
            self.out.getvalue()
        )
        for nb, val in [(EcuRefBase.objects.count(), 4), (EcuModel.objects.count(), 5), (EcuType.objects.count(), 4)]:
            self.assertEqual(nb, val)

        # Clear EcuRefBase, EcuModel and EcuType tables
        call_command('clearreman', '--ecurefbase', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table EcuRefBase terminée!",
            self.out.getvalue()
        )
        for obj_nb in [EcuRefBase.objects.count(), EcuModel.objects.count(), EcuType.objects.count()]:
            self.assertEqual(obj_nb, 0)

    def test_send_email_batch(self):
        call_command("emailreman", "--batch",  stdout=self.out)
        self.assertIn("Pas de lot REMAN en cours à envoyer !", self.out.getvalue())

    def test_export_reman_files(self):
        call_command("exportreman", "--batch", stdout=self.out)
        self.assertIn("[BATCH] Export completed", self.out.getvalue())
        self.assertIn(os.path.join(CSD_ROOT, conf.BATCH_EXPORT_FILE), self.out.getvalue())

        call_command("exportreman", "--repair", stdout=self.out)
        self.assertIn("[REPAIR] Export completed", self.out.getvalue())
        self.assertIn(os.path.join(CSD_ROOT, conf.REPAIR_EXPORT_FILE), self.out.getvalue())

        call_command("exportreman", "--check_out", stdout=self.out)
        self.assertIn("[CHECK_OUT] Export completed", self.out.getvalue())
        self.assertIn(os.path.join(CSD_ROOT, conf.CHECKOUT_EXPORT_FILE), self.out.getvalue())

        call_command("exportreman", "--cal_ecu", stdout=self.out)
        self.assertIn("[ECU_CAL] Export completed", self.out.getvalue())
        self.assertIn("liste_CAL_PSA.txt", self.out.getvalue())

        call_command("exportreman", "--scan_in_out", stdout=self.out)
        self.assertIn("[SCAN_IN_OUT] Export completed", self.out.getvalue())
        self.assertIn(os.path.join(CSD_ROOT, conf.SCAN_IN_OUT_EXPORT_FILE), self.out.getvalue())
