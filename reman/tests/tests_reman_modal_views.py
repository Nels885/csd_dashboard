from dashboard.tests.base import UnitTest, reverse

from reman.models import EcuModel, Batch, Repair, EcuRefBase


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        ref_base = EcuRefBase.objects.create(reman_reference='1234567890')
        ecu = EcuModel.objects.create(oe_raw_reference='1699999999', hw_reference='9876543210', technical_data='test',
                                      ecu_ref_base=ref_base)
        batch = Batch.objects.create(year="C", number=1, quantity=10, created_by=self.user, ecu_ref_base=ref_base)
        self.add_perms_user(Batch, 'add_batch')
        self.add_perms_user(Repair, 'add_repair')
        self.ecuId = ecu.id

    def test_create_batch_ajax_mixin(self):
        """
        Create Batch through BSModalCreateView.
        """
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('reman:create_batch'),
            data={
                'number': '2',
                'quantity': '20',
                'start_date': '02/01/1970',
                'end_date': '01/01/1970',
                'ref_reman': ''
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        batchs = Batch.objects.all()
        self.assertEqual(batchs.count(), 1)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('reman:create_batch'),
            data={
                'number': '2',
                'quantity': '20',
                'start_date': '01/01/1970',
                'end_date': '01/01/1970',
                'ref_reman': '1234567890'
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        batchs = Batch.objects.all()
        self.assertEqual(batchs.count(), 2)

    # def test_create_repair_ajax_mixin(self):
    #     """
    #     Create Repair through BSModalCreateView.
    #     """
    #     self.login()
    #
    #     # First post request = ajax request checking if form in view is valid
    #     response = self.client.post(
    #         reverse('reman:create_repair'),
    #         data={
    #             'ref_psa': '',
    #             'identify_number': '',
    #             'ref_supplier': '1234567890',
    #             'product_number': '1234567890',
    #             'remark': 'test',
    #         },
    #         HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    #     )
    #
    #     # Form has errors
    #     self.assertTrue(response.context_data['form'].errors)
    #     # No redirection
    #     self.assertEqual(response.status_code, 200)
    #     # Object is not created
    #     repairs = Repair.objects.all()
    #     self.assertEqual(repairs.count(), 0)
    #
    #     # Second post request = non-ajax request creating an object
    #     response = self.client.post(
    #         reverse('reman:create_repair'),
    #         data={
    #             'ref_psa': '9876543210',
    #             'identify_number': 'C001010001',
    #             'ref_supplier': '1234567890',
    #             'product_number': '1234567890',
    #             'remark': 'test',
    #         },
    #     )
    #
    #     # redirection
    #     self.assertEqual(response.status_code, 302)
    #     # Object is not created
    #     repairs = Repair.objects.all()
    #     self.assertEqual(repairs.count(), 1)
