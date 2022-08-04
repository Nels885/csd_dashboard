from django.core.management import call_command
from constance import config
from io import StringIO

from dashboard.tests.base import UnitTest
from squalaetp.models import ProductCode, Xelon
from utils.conf import string_to_list


class XelonCommandTestCase(UnitTest):

    def setUp(self):
        super(type(self), self).setUp()
        self.out = StringIO()

    def test_loadsparepart_cmd(self):
        call_command('loadsparepart', '-f' 'dashboard/tests/files/extraction_test.csv', stdout=self.out)
        self.assertIn(
            "[SPAREPART] Data update completed: CSV_LINES = 2 | ADD = 2 | UPDATE = 0 | TOTAL = 2",
            self.out.getvalue()
        )
        self.assertEqual(ProductCode.objects.count(), 2)

        call_command('clearsqualaetp', '--parts', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table SparePart terminée!",
            self.out.getvalue(),
        )
        self.assertEqual(ProductCode.objects.count(), 0)

    def test_loadsqualaetp_cmd(self):

        # Test for files not found
        call_command(
            'loadsqualaetp', '--xelon_update', '-S' 'test.xls', '-D' 'test.xls, test.xls', '-T', 'test.xls',
            stdout=self.out
        )
        self.assertIn(
            "[SQUALAETP_FILE] FileNotFoundError: [Errno 2] No such file or directory: 'test.xls", self.out.getvalue())
        self.assertIn(
            "[DELAY_FILE] FileNotFoundError: [Errno 2] No such file or directory: 'test.xls'", self.out.getvalue())
        self.assertIn(
            "[DELAY_FILE] FileNotFoundError: [Errno 2] No such file or directory: 'test.xls'", self.out.getvalue())

        # Test for relationships option
        call_command('loadsqualaetp', '--relations', stdout=self.out)
        self.assertIn("[SQUALAETP] Relationships update completed: CORVET/XELON", self.out.getvalue())
        self.assertIn("[SQUALAETP] Relationships update completed: CATEGORY/XELON", self.out.getvalue())

        # Test for product category option
        call_command('loadsqualaetp', '--prod_category', stdout=self.out)
        self.assertIn("[SQUALAETP] ProductCategory update completed:", self.out.getvalue())

        # Test for Xelon name update option
        call_command('loadsqualaetp', '--xelon_name_update', stdout=self.out)
        self.assertIn("[ECU & MEDIA] Waiting...", self.out.getvalue())
        self.assertIn("[ECU & MEDIA] data update completed:", self.out.getvalue())

    def test_importcorvet_cmd(self):
        Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                             modele_vehicule='peugeot')

        call_command('importcorvet', '--test', '--squalaetp', stdout=self.out)
        self.assertIn("[IMPORT_CORVET] Import completed:", self.out.getvalue())

        call_command('importcorvet', '--test', '--all', stdout=self.out)
        self.assertIn("[IMPORT_CORVET] Import completed:", self.out.getvalue())

        call_command('importcorvet', '--test', stdout=self.out)
        self.assertIn("[IMPORT_CORVET] Import completed:", self.out.getvalue())

        call_command('importcorvet', '--test', self.vin, stdout=self.out)
        self.assertIn("Corvet login Error !!!", self.out.getvalue())

        call_command('importcorvet', '--test', '--immat', 'ABCDE', stdout=self.out)
        self.assertIn("Corvet login Error !!!", self.out.getvalue())

    def test_clear_squalaetp_xelon_table(self):
        call_command('clearsqualaetp', '--xelon', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Xelon terminée!",
            self.out.getvalue()
        )

    def test_clear_squalaetp_indicator_table(self):
        call_command('clearsqualaetp', '--indicator', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table Indicator terminée!",
            self.out.getvalue()
        )

    def test_clear_squalaetp_product_category_table(self):
        call_command('clearsqualaetp', '--prod_category', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table ProductCategory terminée!",
            self.out.getvalue()
        )

    def test_clear_squalaetp_user_skills_relation(self):
        call_command('clearsqualaetp', '--user_skills', stdout=self.out)
        self.assertIn(
            "Suppression des données polyvavence produits terminée!",
            self.out.getvalue()
        )

    def test_clear_squalaetp_sparepart_table(self):
        call_command('clearsqualaetp', '--parts', stdout=self.out)
        self.assertIn(
            "Suppression des données de la table SparePart terminée!",
            self.out.getvalue()
        )

    def test_clear_squalaetp_part_relations_table(self):
        call_command('clearsqualaetp', '--part_relations', stdout=self.out)
        self.assertIn(
            "Suppression des relations entre les tables ProductCode, Ecu et Media terminée!",
            self.out.getvalue()
        )

    def test_export_squalaetp_files(self):
        call_command('exportsqualaetp', '--corvet', stdout=self.out)
        self.assertIn("[CORVET_EXPORT] Export completed", self.out.getvalue())
        self.assertIn("squalaetp_corvet.csv", self.out.getvalue())

        call_command('exportsqualaetp', stdout=self.out)
        self.assertIn("[SQUALAETP_EXPORT]", self.out.getvalue())
        for filename in string_to_list(config.SQUALAETP_FILE_LIST):
            self.assertIn(filename, self.out.getvalue())
