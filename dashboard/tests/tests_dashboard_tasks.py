from dashboard.tests.base import UnitTest
from dashboard.tasks import (
    cmd_sendemail_all_task, cmd_sendemail_task, cmd_import_excel_task, cmd_loadcontract_task, cmd_database_backup_task
)


class DashboardTaskTestCase(UnitTest):

    def setUp(self):
        super(DashboardTaskTestCase, self).setUp()

    def test_cmd_sendemail_all_task(self):
        response = cmd_sendemail_all_task()
        self.assertDictEqual(response, {"msg": "Envoi des Emails du matin terminés !"})

    def test_cmd_sendemail_task(self):
        response = cmd_sendemail_task("--late_products", "--pending_products", "--vin_error", "--vin_corvet", "--reman")
        self.assertDictEqual(response, {"msg": "Envoi des Emails produits en cours terminés !"})

    def test_cmd_loadcontract_task(self):
        response = cmd_loadcontract_task()
        self.assertIn("[CONTRACT] Path to excel file missing !", response)

        response = cmd_loadcontract_task("-f", "test.xlsx")
        self.assertIn("[CONTRACT] No excel file found", response)

    def test_cmd_database_backup_task(self):
        response = cmd_database_backup_task()
        self.assertIn(
            "CommandError: Unable to serialize database: [Errno 2] No such file or directory:", response["msg"])

        response = cmd_database_backup_task(base_dir="~/Documents/CSD_DATABASE/EXTS/")
        self.assertDictEqual(response, {"msg": "Backup database success!"})

    def test_cmd_import_excel_task(self):
        response = cmd_import_excel_task()
        self.assertIn("[IMPORT_EXCEL] Update completed.", response.get("importexcel"))
        self.assertIn("[SPAREPART_FILE] FileNotFoundError:", response.get("loadsparepart"))
        self.assertIn("[IMPORT_CORVET] Import completed:", response.get("importcorvet"))
