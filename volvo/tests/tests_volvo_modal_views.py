from django.contrib.messages import get_messages

from dashboard.tests.base import UnitTest, reverse

from volvo.models import SemRefBase, SemModel, SemType


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        sem_type = SemType.objects.create(asm_reference='9876543210', hw_reference='9876543210', technical_data='test')
        ref_base = SemRefBase.objects.create(reman_reference='1234567890', ecu_type=sem_type)
        sem = SemModel.objects.create(pf_code_oe='PF987654AA', pi_code_oe='PI987654AA', ecu_type=sem_type)
        self.semId = sem.id
        self.semRefBase = ref_base

    def test_create_sem_hw_ajax_mixin(self):
        """
        Create ECU Type throught BSModalUpdateView.
        """
        self.add_perms_user(SemType, 'add_semtype')
        self.login()

        # First post request = ajax request checking if form in view is valid
        for asm_ref, hw_ref in [('', ''), ('0123456789', ''), ('9876543210', '9876543211')]:
            response = self.client.post(
                reverse('volvo:sem_hw_create'),
                data={
                    'asm_referecne': asm_ref,
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
            sem_type = SemType.objects.all()
            self.assertEqual(sem_type.count(), 1)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('volvo:sem_hw_create'),
            data={
                'asm_reference': '1234567890',
                'hw_reference': '9876543210',
                'technical_data': 'SEM',
                'supplier_oe': 'PARROT',
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        sem_type = SemType.objects.all()
        self.assertEqual(sem_type.count(), 2)
        self.assertEqual(sem_type.last().asm_reference, '1234567890')
        self.assertEqual(sem_type.last().hw_reference, '9876543210')

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
        self.add_perms_user(SemRefBase, 'add_semrefbase')
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
            sem_type = SemType.objects.all()
            self.assertEqual(sem_type.count(), 1)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('volvo:reman_ref_create'),
            data={
                'reman_reference': '1234567891',
                'asm_reference': '9876543210'
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        remans = SemRefBase.objects.all()
        self.assertEqual(remans.count(), 2)
        self.assertEqual(remans.last().reman_reference, '1234567891')
