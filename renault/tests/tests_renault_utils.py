import unittest

from renault.utils import derive_precode


class TestRenaultUtils(unittest.TestCase):

    def test_derive_precode(self):
        self.assertEqual(derive_precode("S053"), "7913")
        self.assertEqual(derive_precode("V188"), "4839")
        self.assertEqual(derive_precode("Q420"), "9588")
