from django.core.management import call_command
from io import StringIO

from dashboard.tests.base import UnitTest


class PsaCommandTestCase(UnitTest):

    def setUp(self):
        super(type(self), self).setUp()
        self.out = StringIO()
        self.delMsg = "Deleting data from table {0} completed !"

    def test_clear_psa_multimedia_table(self):
        call_command('clearpsa', '--multimedia', stdout=self.out)
        self.assertIn(self.delMsg.format('Multimedia'), self.out.getvalue())

    def test_clear_psa_ecu_table(self):
        call_command('clearpsa', '--ecu', stdout=self.out)
        self.assertIn(self.delMsg.format('Ecu'), self.out.getvalue())

    def test_clear_psa_corvet_table(self):
        call_command('clearpsa', '--corvet', stdout=self.out)
        self.assertIn(self.delMsg.format('Corvet'), self.out.getvalue())

    def test_clear_psa_defaultcode_table(self):
        call_command('clearpsa', '--dtc', stdout=self.out)
        self.assertIn(self.delMsg.format('DefaultCode'), self.out.getvalue())

    def test_clear_psa_corvet_attribute_table(self):
        call_command('clearpsa', '--corvet_attribute', stdout=self.out)
        self.assertIn(self.delMsg.format('CorvetAttribute'), self.out.getvalue())

    def test_clear_psa_canremote_table(self):
        call_command('clearpsa', '--canremote', stdout=self.out)
        self.assertIn(self.delMsg.format('CanRemote'), self.out.getvalue())

    def test_cmd_loadsqualaetp(self):
        # Test for files not found
        call_command('loadcorvet', '-f' 'test.xls', stdout=self.out)
        self.assertIn("[CORVET_CMD] No squalaetp file found", self.out.getvalue())

        call_command('loadcorvet', '--import_csv', stdout=self.out)
        self.assertIn("[CORVET_CMD] Missing CSV file", self.out.getvalue())

        call_command('loadcorvet', '--import_csv', '-f', 'test.xls', stdout=self.out)
        self.assertIn("[CORVET_CMD] No CSV file found", self.out.getvalue())

        call_command('loadcorvet', '--attribute', '-f', 'test.xls', stdout=self.out)
        self.assertIn("[CORVET_CMD] No Attribute file found", self.out.getvalue())

        # Test of relationship into Corvet and CorvetProduct
        call_command('loadcorvet', '--relations', stdout=self.out)
        self.assertIn("[CORVET_CMD] Relationships update completed:", self.out.getvalue())
