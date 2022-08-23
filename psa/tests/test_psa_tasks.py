from celery.contrib.testing.worker import start_worker
from django.test import TransactionTestCase

from sbadmin.celery import app

from dashboard.tests.base import UnitTest
from psa.tasks import save_corvet_to_models, import_corvet_task, import_corvet_list_task


class PsaTaskTestCase(TransactionTestCase):

    def setUp(self):
        super(PsaTaskTestCase, self).setUp()
        self.celery_worker = start_worker(app, perform_ping_check=False)
        self.celery_worker.__enter__()
        self.vin = 'VF3ABCDEF12345678'

    def tearDown(self):
        super().tearDown()
        self.celery_worker.__exit__(None, None, None)

    def test_save_corvet_to_models_task(self):
        response = save_corvet_to_models("ABCDE")
        self.assertEqual(response, "ABCDE Not VIN PSA")

        response = save_corvet_to_models(self.vin)
        self.assertIn(f"{self.vin} error CORVET in", response)

    def test_import_corvet_task(self):
        task = import_corvet_task.delay("ABCDE")
        self.assertEqual(task.get(), "ABCDE Not VIN PSA")

        task = import_corvet_task.delay(self.vin)
        self.assertIn(f"{self.vin} error CORVET", task.get())

    def test_import_corvet_list_task(self):
        task = import_corvet_list_task.delay("ABCDE")
        self.assertDictEqual(task.get(), {
            "detail": "Successfully import VIN PSA",
            "message": "ABCDE Not VIN PSA\r\n"
        })

        task = import_corvet_list_task.delay(self.vin)
        result = task.get()
        self.assertIn(f"{self.vin} error CORVET in", result['message'])
