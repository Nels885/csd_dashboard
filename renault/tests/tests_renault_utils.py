import unittest

from renault.utils import derive_precode


class TestRenaultUtils(unittest.TestCase):

    def test_derive_precode(self):
        data_error = {'result': 'ERROR', 'message': 'Could not compute the code with a empty precode !'}

        # Result OK
        self.assertEqual(derive_precode("S053"), {'result': 'OK', 'code': '7913'})
        self.assertEqual(derive_precode("V188"), {'result': 'OK', 'code': '4839'})
        self.assertEqual(derive_precode("Q420"), {'result': 'OK', 'code': '9588'})

        # Result ERROR
        self.assertEqual(derive_precode(""), data_error)
        self.assertEqual(derive_precode("123456"), data_error)
