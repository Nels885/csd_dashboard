from django.urls import reverse
from django.contrib.messages import get_messages

from reman.tests import RemanTest
from reman.models import EcuModel, Batch, Repair, EcuRefBase, EcuType, Default


class MixinsTest(RemanTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        self.remans = [("PSA", "1234567890"), ("VOLVO", "85123456")]

    def test_create_batch_ajax_mixin(self):
        """
        Create Batch through BSModalCreateView.
        """
        self.add_perms_user(Batch, 'add_batch')
        self.login()

        for reman_type, ref_reman in self.remans:
            # First post request = ajax request checking if form in view is valid
            response = self.client.post(
                reverse('reman:create_batch'),
                data={
                    'type': f'REMAN_{reman_type}',
                    'number': '2',
                    'quantity': '20',
                    'box_quantity': '6',
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
            batchs = Batch.objects.filter(customer=reman_type)
            self.assertEqual(batchs.count(), 1)

            # Second post request = ajax request checking if form in view is valid
            response = self.client.post(
                reverse('reman:create_batch'),
                data={
                    'type': f'REMAN_{reman_type}',
                    'number': '900',
                    'quantity': '20',
                    'box_quantity': '6',
                    'start_date': '01/01/1970',
                    'end_date': '01/01/1970',
                    'ref_reman': ref_reman
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

            # Form has errors
            self.assertTrue(response.context_data['form'].errors)
            # No redirection
            self.assertEqual(response.status_code, 200)
            # Object is not created
            batchs = Batch.objects.filter(customer=reman_type)
            self.assertEqual(batchs.count(), 1)

            # Third post request = non-ajax request creating an object
            response = self.client.post(
                reverse('reman:create_batch'),
                data={
                    'type': f'REMAN_{reman_type}',
                    'number': '2',
                    'quantity': '20',
                    'box_quantity': '6',
                    'start_date': '01/01/1970',
                    'end_date': '01/01/1970',
                    'ref_reman': ref_reman
                },
            )

            # redirection
            self.assertEqual(response.status_code, 302)
            # Object is not created
            batchs = Batch.objects.filter(customer=reman_type)
            self.assertEqual(batchs.count(), 2)

    def test_create_etude_batch_ajax_mixin(self):
        """
        Create Batch through BSModalCreateView.
        """
        self.add_perms_user(Batch, 'add_batch')
        self.login()

        for reman_type, ref_reman in self.remans:
            # First post request = ajax request checking if form in view is valid
            response = self.client.post(
                reverse('reman:create_batch'),
                data={
                    'type': f'ETUDE_{reman_type}',
                    'number': '2',
                    'quantity': '20',
                    'box_quantity': '6',
                    'start_date': '01/01/1970',
                    'end_date': '01/01/1970',
                    'ref_reman': ref_reman
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

            # Form has errors
            self.assertTrue(response.context_data['form'].errors)
            # No redirection
            self.assertEqual(response.status_code, 200)
            # Object is not created
            batchs = Batch.objects.filter(customer=reman_type)
            self.assertEqual(batchs.count(), 1)

            # Second post request = non-ajax request creating an object
            response = self.client.post(
                reverse('reman:create_batch'),
                data={
                    'type': f'ETUDE_{reman_type}',
                    'number': '901',
                    'quantity': '20',
                    'box_quantity': '6',
                    'start_date': '01/01/1970',
                    'end_date': '01/01/1970',
                    'ref_reman': ref_reman
                },
            )

            # redirection
            self.assertEqual(response.status_code, 302)
            # Object is not created
            batchs = Batch.objects.filter(customer=reman_type)
            self.assertEqual(batchs.count(), 2)
            self.assertEqual(batchs.last().number, 901)

    def test_update_batch_ajax_mixin(self):
        """
        Update batch throught BSModalUpdateView.
        """
        self.add_perms_user(Batch, 'change_batch')
        self.login()

        # Update object through BSModalUpdateView
        old_batch = Batch.objects.create(number=99, quantity=20, batch_number='G099020000', created_by=self.user)
        response = self.client.post(
            reverse('reman:update_batch', kwargs={'pk': old_batch.pk}),
            data={
                'box_quantity': '6',
                'active': True,
                'is_barcode': True,
                'start_date': '01/01/1970',
                'end_date': '01/01/1970',
            },
        )
        # redirection
        self.assertRedirects(response, reverse('reman:batch_table') + "?filter=pending", status_code=302)
        # Object is updated
        new_batch = Batch.objects.get(pk=old_batch.pk)
        self.assertNotEqual(new_batch.is_barcode, old_batch.is_barcode)

    def test_update_etude_batch_ajax_mixin(self):
        """
        Update etude batch throught BSModalUpdateView.
        """
        self.add_perms_user(Batch, 'change_batch')
        self.login()

        # Update Batch under etude through BSModalUpdateView
        old_batch = Batch.objects.create(number=999, quantity=20, batch_number='G999020000', created_by=self.user)
        response = self.client.post(
            reverse('reman:update_batch', kwargs={'pk': old_batch.pk}),
            data={
                'box_quantity': '6',
                'active': True,
                'is_barcode': True,
                'start_date': '01/01/1970',
                'end_date': '01/01/1970',
            },
        )
        # redirection
        self.assertRedirects(response, reverse('reman:batch_table') + "?filter=etude", status_code=302)
        # Object is updated
        new_batch = Batch.objects.get(pk=old_batch.pk)
        self.assertNotEqual(new_batch.is_barcode, old_batch.is_barcode)

    def test_Delete_batch_ajax_mixin(self):
        """
        Delete object through BSModalDeleteView.
        """
        self.add_perms_user(Batch, 'delete_batch')
        self.login()

        # Request to delete view passes message to the response
        batch = Batch.objects.first()
        response = self.client.post(reverse('reman:delete_batch', kwargs={'pk': batch.pk}))
        messages = get_messages(response.wsgi_request)
        self.assertEqual(len(messages), 1)

    def test_create_repair_ajax_mixin(self):
        """
        Create Repair through BSModalCreateView.
        """
        self.add_perms_user(Repair, 'add_repair')
        self.login()

        # First post request = non-ajax request creating an object
        response = self.client.post(
            reverse('reman:create_repair'),
            data={
                'barcode': '',
                'identify_number': '',
                'remark': 'test',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        repairs = Repair.objects.all()
        self.assertEqual(repairs.count(), 0)

        # Second post request = ajax request checking if form in view is valid
        for barcode, identify_nb in [('9876543210', 'C001002001'), ('9876543210azertyuiop', 'C001002002')]:
            response = self.client.post(
                reverse('reman:create_repair'),
                data={
                    'barcode': barcode,
                    'identify_number': identify_nb,
                    'remark': 'test',
                },
            )
            # redirection
            self.assertEqual(response.status_code, 302)

        # Object is created
        repairs = Repair.objects.all()
        self.assertEqual(repairs.count(), 2)

    def test_filter_checkout_ajax_mixin(self):
        self.add_perms_user(Repair, 'close_repair')
        self.login()

        # First search request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('reman:out_filter'),
            data={
                'batch': '',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)

        # Second search request = non-ajax request creating an object
        Repair.objects.create(identify_number='C001002001', barcode='9876543210', status='Réparé',
                              quality_control=True, created_by=self.user, batch=self.psaBatch)
        Repair.objects.create(identify_number='V001002001', barcode='PF832200DF', status='Réparé',
                              quality_control=True, created_by=self.user, batch=self.psaBatch)
        for batch in ['C001002000', 'V001002000']:
            response = self.client.post(
                reverse('reman:out_filter'),
                data={
                    'batch': batch,
                },
            )

            # redirection
            self.assertEqual(response.status_code, 302)

    def test_update_ecu_dump_ajax_mixin(self):
        """
        Update ECU Dump throught BSModalUpdateView.
        """
        self.add_perms_user(EcuModel, 'change_ecumodel')
        self.login()

        # Update object through BSModalUpdateView
        ecu_model = EcuModel.objects.first()
        response = self.client.post(
            reverse('reman:update_ecu_dump', kwargs={'pk': ecu_model.pk}),
            data={
                'barcode': ecu_model.barcode,
                'to_dump': True,
            }
        )
        # redirection
        self.assertRedirects(response, reverse('reman:ecu_dump_table'), status_code=302)
        # Object is updated
        ecu_model = EcuModel.objects.first()
        self.assertEqual(ecu_model.to_dump, True)

    def test_create_ecu_hw_ajax_mixin(self):
        """
        Create ECU Type throught BSModalUpdateView.
        """
        self.add_perms_user(EcuType, 'add_ecutype')
        self.login()

        # First post request = ajax request checking if form in view is valid
        for hw_ref, tech_data in [('', ''), ('0123456789', ''), ('9876543210', 'test_new')]:
            response = self.client.post(
                reverse('reman:ecu_hw_create'),
                data={
                    'hw_reference': hw_ref,
                    'hw_type': 'ECU',
                    'technical_data': tech_data,
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

            # Form has errors
            self.assertTrue(response.context_data['form'].errors)
            # No redirection
            self.assertEqual(response.status_code, 200)
            # Object is not created
            ecu_type = EcuType.objects.filter(hw_type='ECU')
            self.assertEqual(ecu_type.count(), 1)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('reman:ecu_hw_create'),
            data={
                'hw_reference': '1234567890',
                'hw_type': 'ECU',
                'technical_data': 'test',
                'status': 'test'
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        ecu_type = EcuType.objects.filter(hw_type='ECU')
        self.assertEqual(ecu_type.count(), 2)
        self.assertEqual(ecu_type.last().hw_reference, '1234567890')

    def test_update_ecu_hw_ajax_mixin(self):
        """
        Update ECU Type throught BSModalUpdateView.
        """
        self.add_perms_user(EcuType, 'change_ecutype')
        self.login()

        # Update object through BSModalUpdateView
        ecu_type = EcuType.objects.filter(hw_type='ECU').first()
        response = self.client.post(
            reverse('reman:ecu_hw_update', kwargs={'pk': ecu_type.pk}),
            data={
                'hw_reference': ecu_type.hw_reference,
                'hw_type': 'ECU',
                'technical_data': 'test_new',
            }
        )
        # redirection
        self.assertRedirects(response, reverse('reman:ecu_hw_table'), status_code=302)
        # Object is updated
        ecu_type = EcuType.objects.first()
        self.assertEqual(ecu_type.technical_data, 'test_new')

    def test_create_sem_hw_ajax_mixin(self):
        """
        Create ECU Type throught BSModalUpdateView.
        """
        self.add_perms_user(EcuType, 'add_ecutype')
        self.login()

        # First post request = ajax request checking if form in view is valid
        for hw_ref, tech_data in [('', ''), ('0123456789', ''), ('85023924.P01', 'SEM_new')]:
            response = self.client.post(
                reverse('reman:ecu_hw_create'),
                data={
                    'hw_reference': hw_ref,
                    'hw_type': 'NAV',
                    'technical_data': tech_data,
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

            # Form has errors
            self.assertTrue(response.context_data['form'].errors)
            # No redirection
            self.assertEqual(response.status_code, 200)
            # Object is not created
            ecu_type = EcuType.objects.filter(hw_type='NAV')
            self.assertEqual(ecu_type.count(), 1)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('reman:ecu_hw_create'),
            data={
                'hw_reference': '85023925.P01',
                'hw_type': 'NAV',
                'technical_data': 'SEM',
                'supplier_oe': 'PARROT'
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        ecu_type = EcuType.objects.filter(hw_type='NAV')
        self.assertEqual(ecu_type.count(), 2)
        self.assertEqual(ecu_type.last().hw_reference, '85023925.P01')

    def test_update_sem_hw_ajax_mixin(self):
        """
        Update SEM Type throught BSModalUpdateView.
        """
        self.add_perms_user(EcuType, 'change_ecutype')
        self.login()

        # Update object through BSModalUpdateView
        ecu_type = EcuType.objects.filter(hw_type='NAV').first()
        response = self.client.post(
            reverse('reman:ecu_hw_update', kwargs={'pk': ecu_type.pk}),
            data={
                'hw_reference': ecu_type.hw_reference,
                'hw_type': 'NAV',
                'technical_data': 'SEM_new',
            }
        )
        # redirection
        self.assertRedirects(response, reverse('reman:ecu_hw_table'), status_code=302)
        # Object is updated
        ecu_type = EcuType.objects.filter(hw_type='NAV').first()
        self.assertEqual(ecu_type.technical_data, 'SEM_new')

    def test_create_ref_reman_ajax_mixin(self):
        """
        Create EcuRefBase throught BSModalUpdateView.
        """
        self.add_perms_user(EcuRefBase, 'add_ecurefbase')
        self.login()

        # First post request = ajax request checking if form in view is valid
        refs_list = [('', ''), ('1234567890', '9876543210'), ('1234567891', ''), ('1234567891', 'test_new')]
        for reman_ref, hw_ref in refs_list:
            response = self.client.post(
                reverse('reman:ref_reman_create'),
                data={
                    'reman_reference': reman_ref,
                    'hw_reference': hw_ref
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

            # Form has errors
            self.assertTrue(response.context_data['form'].errors)
            # No redirection
            self.assertEqual(response.status_code, 200)
            # Object is not created
            ecu_type = EcuType.objects.all()
            self.assertEqual(ecu_type.count(), 2)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('reman:ref_reman_create'),
            data={
                'reman_reference': '1234567891',
                'hw_reference': '9876543210',
                'status': 'test'
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        remans = EcuRefBase.objects.all()
        self.assertEqual(remans.count(), 3)
        self.assertEqual(remans.last().reman_reference, '1234567891')
        self.assertEqual(remans.last().status, 'test')
