from django.core.management import call_command
from django.test import TestCase

from io import StringIO


class ProgCommandTestCase(TestCase):

    def setUp(self):
        super(type(self), self).setUp()
        self.out = StringIO()
        self.delMsg = "Deleting data from {0} table completed !"

    def test_clear_prog_raspeedi_table(self):
        call_command('clearprog', '--raspeedi', stdout=self.out)
        self.assertIn(self.delMsg.format('Raspeedi'), self.out.getvalue())

    def test_clear_prog_programing_table(self):
        call_command('clearprog', '--programing', stdout=self.out)
        self.assertIn(self.delMsg.format('Programing'), self.out.getvalue())
