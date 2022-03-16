from dashboard.tests.base import UnitTest

from reman.models import Repair, SparePart, Batch, EcuModel, EcuRefBase, EcuType, Default


class RemanTest(UnitTest):

    def setUp(self):
        super().setUp()
        spare_part = SparePart.objects.create(code_produit='test HW_9876543210')
        self.authError = {"detail": "Informations d'authentification non fournies."}
        Default.objects.create(code='TEST1', description='Ceci est le test 1')

        # PSA REMAN
        self.barcode = '9612345678'
        psa_type = EcuType.objects.create(hw_reference='9876543210', technical_data='test', spare_part=spare_part)
        psa_base = EcuRefBase.objects.create(reman_reference='1234567890', ecu_type=psa_type)
        EcuModel.objects.create(barcode=self.barcode, oe_raw_reference='1699999999', ecu_type=psa_type)
        EcuModel.objects.create(barcode='9876543210', oe_raw_reference='1699999999', ecu_type=psa_type)
        EcuModel.objects.create(barcode='9876543210azertyuiop', ecu_type=psa_type)
        self.psaRefBase = psa_base
        self.psaBatch = Batch.objects.create(year="C", number=1, quantity=2, created_by=self.user, ecu_ref_base=psa_base)

        # VOLVO REMAN
        sem_type = EcuType.objects.create(hw_reference='85023924.P01', hw_type='NAV', technical_data='SEM')
        sem_base = EcuRefBase.objects.create(
            reman_reference='85123456', brand='VOLVO', pf_code='PF832706GK', ecu_type=sem_type)
        EcuModel.objects.create(barcode='PF832200DF', oe_raw_reference='22996488.P02', ecu_type=sem_type)
        self.semBatch = Batch.objects.create(
            year="V", number=1, quantity=2, customer="VOLVO", created_by=self.user, ecu_ref_base=sem_base)
