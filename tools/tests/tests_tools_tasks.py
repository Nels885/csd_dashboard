from dashboard.tests.base import UnitTest
from tools.tasks import cmd_infotech_task, cmd_suptech_task


class ToolsTaskTestCase(UnitTest):

    def setUp(self):
        super().setUp()

    def test_cmd_suptech_task(self):
        response = cmd_suptech_task("--email")
        self.assertIn("Pas de Suptech en cours à envoyer !", response)

    def test_cmd_infotech_task(self):
        response = cmd_infotech_task("--email")
        self.assertIn("Pas d'Infotech en cours à envoyer !", response)
