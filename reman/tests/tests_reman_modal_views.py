from django.contrib.messages import get_messages

from dashboard.tests.base import UnitTest, reverse

from reman.models import EcuModel, Batch, Repair, EcuRefBase, EcuType, Default


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        ecu_type = EcuType.objects.create(hw_reference='9876543210', technical_data='test')
        ref_base = EcuRefBase.objects.create(reman_reference='1234567890', ecu_type=ecu_type)
        ecu = EcuModel.objects.create(oe_raw_reference='1699999999', psa_barcode='9876543210', ecu_type=ecu_type)
        self.batch = Batch.objects.create(year="C", number=1, quantity=1, created_by=self.user, ecu_ref_base=ref_base)
        Default.objects.create(code='TEST1', description='Ceci est le test 1')
        self.ecuId = ecu.id
        self.refBaseId = ref_base.id

    def test_create_batch_ajax_mixin(self):
        """
        Create Batch through BSModalCreateView.
        """
        self.add_perms_user(Batch, 'add_batch')
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

    def test_create_etude_batch_ajax_mixin(self):
        """
        Create Batch through BSModalCreateView.
        """
        self.add_perms_user(Batch, 'add_batch')
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('reman:create_etude_batch'),
            data={
                'number': '2',
                'quantity': '20',
                'start_date': '01/01/1970',
                'end_date': '01/01/1970',
                'ref_reman': '1234567890'
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
            reverse('reman:create_etude_batch'),
            data={
                'number': '901',
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
        self.assertEqual(batchs.last().number, 901)

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

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('reman:create_repair'),
            data={
                'psa_barcode': '',
                'identify_number': '',
                'ref_supplier': '1234567890',
                'product_number': '1234567890',
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

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('reman:create_repair'),
            data={
                'psa_barcode': '9876543210',
                'identify_number': 'C001001001',
                'ref_supplier': '1234567890',
                'product_number': '1234567890',
                'remark': 'test',
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        repairs = Repair.objects.all()
        self.assertEqual(repairs.count(), 1)

    def test_create_default_ajax_mixin(self):
        """
        Create Default through BSModalCreateView.
        """
        self.add_perms_user(Default, 'add_default')
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('reman:create_default'),
            data={
                'code': '',
                'description': '',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        defaults = Default.objects.all()
        self.assertEqual(defaults.count(), 1)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('reman:create_default'),
            data={
                'code': 'TEST2',
                'description': 'Ceci est le test 2',
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        defaults = Default.objects.all()
        self.assertEqual(defaults.count(), 2)

    def test_update_default_ajax_mixin(self):
        """
        Update Default throught BSModalUpdateView.
        """
        self.add_perms_user(Default, 'change_default')
        self.login()

        # Update object through BSModalUpdateView
        default = Default.objects.first()
        response = self.client.post(
            reverse('reman:update_default', kwargs={'pk': default.pk}),
            data={
                'code': 'TEST3',
                'description': 'Ceci est le test 3',
            }
        )
        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is updated
        default = Default.objects.first()
        self.assertEqual(default.code, 'TEST3')

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
        Repair.objects.create(identify_number='C001001001', psa_barcode='9876543210', status='Réparé',
                              quality_control=True, created_by=self.user, batch=self.batch)
        response = self.client.post(
            reverse('reman:out_filter'),
            data={
                'batch': 'C001001000',
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
                'psa_barcode': ecu_model.psa_barcode,
                'to_dump': True,
            }
        )
        # redirection
        self.assertRedirects(response, reverse('reman:ecu_dump_table'), status_code=302)
        # Object is updated
        ecu_model = EcuModel.objects.first()
        self.assertEqual(ecu_model.to_dump, True)
