from dashboard.tests.base import UnitTest
from constance.test import override_config
from squalaetp.tasks import (
    cmd_loadsqualaetp_task, cmd_exportsqualaetp_task, cmd_importcorvet_task, send_email_task, save_sivin_to_models
)


@override_config(CORVET_USER="")
@override_config(CORVET_PWD="")
@override_config(SYS_REPORT_TO_MAIL_LIST="")
class XelonTaskTestCase(UnitTest):

    def setUp(self):
        super(XelonTaskTestCase, self).setUp()

    def test_cmd_loadsqualaetp_task(self):
        response = cmd_loadsqualaetp_task()
        self.assertDictEqual(response, {
            "msg": "Erreur d'importation Squalaetp, voir l'email du rapport !!", "tags": "warning"
        })

    def test_cmd_exportsqualaetp_task(self):
        response = cmd_exportsqualaetp_task()
        self.assertDictEqual(response, {"msg": "Exportation Squalaetp terminée.", "tags": "success"})

    def test_cmd_importcorvet_task(self):
        response = cmd_importcorvet_task("--test", self.vin)
        self.assertIn("Corvet login Error !!!", response)

    def test_save_sivin_to_models(self):
        response = save_sivin_to_models("ABCDEFG", test=True)
        self.assertIn("ABCDEFG - error SIVIN in", response)

    def test_send_email_task(self):
        response = send_email_task("test", "test", "test@test.com", ["test@test.com"], [])
        self.assertDictEqual(response, {
            "msg": "Envoi email terminé.", "subject": "test", "from_email": "test@test.com", "to": ["test@test.com"]
        })
