from django.contrib.messages import get_messages

from dashboard.tests.base import UnitTest, reverse

from reman.models import EcuRefBase, EcuModel, EcuType


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        sem_type = EcuType.objects.create(hw_reference='9876543210', technical_data='test')
        ref_base = EcuRefBase.objects.create(reman_reference='1234567890', ecu_type=sem_type)
        sem = EcuModel.objects.create(barcode='PF987654AA', oe_reference='PI987654AA', ecu_type=sem_type)
        self.ecuId = sem.id
        self.ecuRefBase = ref_base

    def test_create_sem_hw_ajax_mixin(self):
        """
        Create ECU Type throught BSModalUpdateView.
        """
        self.add_perms_user(EcuType, 'add_ecutype')
        self.login()

        # First post request = ajax request checking if form in view is valid
        for hw_ref in ['', '9876543210']:
            response = self.client.post(
                reverse('volvo:sem_hw_create'),
                data={
                    'hw_reference': hw_ref,
                    'technical_data': 'SEM',
                    'supplier_oe': 'PARROT',
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

            # Form has errors
            self.assertTrue(response.context_data['form'].errors)
            # No redirection
            self.assertEqual(response.status_code, 200)
            # Object is not created
            ecu_type = EcuType.objects.all()
            self.assertEqual(ecu_type.count(), 1)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('volvo:sem_hw_create'),
            data={
                'hw_reference': '1234567890',
                'technical_data': 'SEM',
                'supplier_oe': 'PARROT',
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        ecu_type = EcuType.objects.all()
        self.assertEqual(ecu_type.count(), 2)
        self.assertEqual(ecu_type.last().hw_reference, '1234567890')

    # def test_update_ecu_hw_ajax_mixin(self):
    #     """
    #     Update ECU Type throught BSModalUpdateView.
    #     """
    #     self.add_perms_user(EcuType, 'change_ecutype')
    #     self.login()
    #
    #     # Update object through BSModalUpdateView
    #     ecu_type = EcuType.objects.first()
    #     response = self.client.post(
    #         reverse('reman:ecu_hw_update', kwargs={'pk': ecu_type.pk}),
    #         data={
    #             'hw_reference': ecu_type.hw_reference,
    #             'technical_data': 'test',
    #         }
    #     )
    #     # redirection
    #     self.assertRedirects(response, reverse('reman:ecu_hw_table'), status_code=302)
    #     # Object is updated
    #     ecu_type = EcuType.objects.first()
    #     self.assertEqual(ecu_type.technical_data, 'test')

    def test_create_sem_ref_base_ajax_mixin(self):
        """
        Create SemRefBase throught BSModalUpdateView.
        """
        self.add_perms_user(EcuRefBase, 'add_ecurefbase')
        self.login()

        # First post request = ajax request checking if form in view is valid
        refs_list = [('', ''), ('1234567890', '9876543210'), ('1234567891', ''), ('1234567891', 'test_new')]
        for reman_ref, hw_ref in refs_list:
            response = self.client.post(
                reverse('volvo:reman_ref_create'),
                data={
                    'reman_reference': reman_ref,
                    'asm_reference': hw_ref
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

            # Form has errors
            self.assertTrue(response.context_data['form'].errors)
            # No redirection
            self.assertEqual(response.status_code, 200)
            # Object is not created
            sem_type = EcuType.objects.all()
            self.assertEqual(sem_type.count(), 1)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('volvo:reman_ref_create'),
            data={
                'reman_reference': '1234567891',
                'hw_reference': '9876543210'
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        remans = EcuRefBase.objects.all()
        self.assertEqual(remans.count(), 2)
        self.assertEqual(remans.last().reman_reference, '1234567891')
