from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.translation import ugettext as _

from reman.tests import RemanTest

from reman.models import Repair, SparePart, Batch, EcuModel, EcuRefBase, EcuType, Default


class RemanTestCase(RemanTest):

    def setUp(self):
        super().setUp()
        self.psaRepair = Repair.objects.create(batch=self.psaBatch, identify_number="C001010001",
                                               created_by=self.user, status="Réparé", quality_control=True)
        self.semRepair = Repair.objects.create(
            batch=self.semBatch, identify_number="V001002001", created_by=self.user, status="Réparé",
            quality_control=True, new_barcode='PF832706GK00000001')

    def test_repair_table_page(self):
        url = reverse('reman:repair_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        # Test if connected with permissions
        self.add_perms_user(Repair, 'view_repair')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_spare_part_table_page(self):
        url = reverse('reman:part_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(SparePart, 'view_sparepart')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_repair_pages(self):
        urls_perms = [
            (reverse('reman:create_repair'), 'add_repair'),
            (reverse('reman:edit_repair', kwargs={'pk': self.psaRepair.pk}), 'change_repair'),
            (reverse('reman:close_repair', kwargs={'pk': self.psaRepair.pk}), 'change_repair'),
            (reverse('reman:detail_repair', kwargs={'pk': self.psaRepair.pk}), 'view_repair'),
        ]
        for url, perm in urls_perms:
            response = self.client.get(url)
            self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

            self.add_perms_user(Repair, perm)
            self.login()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_batch_table(self):
        url = reverse('reman:batch_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(Batch, 'view_batch')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_psa_out_table(self):
        url = reverse('reman:out_table') + '?filter=' + self.psaBatch.batch_number
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(Repair, 'close_repair')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Invalid form
        response = self.client.post(url, {'barcode': ''})
        self.assertFormError(response, 'form', 'barcode', _('This field is required.'))
        for barcode in ['C001010001', 'C001010002R', 'PF832706GK00000002']:
            response = self.client.post(url, {'barcode': barcode})
            self.assertFormError(response, 'form', 'barcode', "Code barre ou QR code invalide")
        Repair.objects.create(
            batch=self.psaBatch, identify_number="C001010002", created_by=self.user, status="Réparé")
        response = self.client.post(url, {'barcode': 'C001010002R'})
        self.assertFormError(response, 'form', 'barcode', "Contrôle qualité non validé, voir avec Atelier.")

        # valid form
        response = self.client.post(url, {'barcode': f'{self.psaRepair.identify_number}R'})
        self.assertEqual(response.status_code, 200)
        repair = Repair.objects.get(identify_number=self.psaRepair.identify_number)
        self.assertNotEqual(repair.closing_date, None)
        self.assertEqual(repair.checkout, True)

    def test_sem_out_table(self):
        url = reverse('reman:out_table') + '?filter=' + self.semBatch.batch_number
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(Repair, 'close_repair')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Invalid form
        response = self.client.post(url, {'barcode': ''})
        self.assertFormError(response, 'form', 'barcode', _('This field is required.'))
        for barcode in ['C001010001', 'C001010002R', 'PF832706GK00000002']:
            response = self.client.post(url, {'barcode': barcode})
            self.assertFormError(response, 'form', 'barcode', "Code barre ou QR code invalide")
        Repair.objects.create(
            batch=self.semBatch, identify_number="V001002002", created_by=self.user, status="Réparé",
            new_barcode="PF832706GK00000002"
        )
        response = self.client.post(url, {'barcode': 'PF832706GK00000002'})
        self.assertFormError(response, 'form', 'barcode', "Contrôle qualité non validé, voir avec Atelier.")

        # valid form
        response = self.client.post(url, {'barcode': self.semRepair.new_barcode})
        self.assertEqual(response.status_code, 200)
        repair = Repair.objects.get(identify_number=self.semRepair.identify_number)
        self.assertNotEqual(repair.closing_date, None)
        self.assertEqual(repair.checkout, True)

    def test_check_part(self):
        url = reverse('reman:part_check')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(EcuModel, 'check_ecumodel', 'add_ecumodel')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Invalid form
        response = self.client.post(url, {'barcode': ''})
        self.assertFormError(response, 'form', 'barcode', _('This field is required.'))
        for barcode in ['123456789', '96123']:
            response = self.client.post(url, {'barcode': barcode})
            self.assertFormError(response, 'form', 'barcode', _('The barcode is invalid'))

        # Valid form
        barcode_list = [
            ('9600000000', '9600000000'), ('9687654321', '9687654321'), ('9800000000', '9800000000'),
            ('9887654321', '9887654321'), ('96876543210000000000', '9687654321'), ('89661-0H390', '89661-0H390')
        ]
        for barcode in barcode_list:
            response = self.client.post(url, {'barcode': barcode[0]})
            self.assertRedirects(
                response, reverse('reman:part_create', kwargs={'barcode': barcode[1]}), status_code=302)
        response = self.client.post(url, {'barcode': self.barcode})
        ecu = EcuModel.objects.get(barcode=self.barcode)
        self.assertEquals(response.context['ecu'], ecu)

    def test_new_part_email(self):
        url = reverse('reman:part_email', kwargs={'barcode': self.barcode})
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(EcuModel, 'check_ecumodel')
        self.login()
        response = self.client.get(url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), _('Success: The email has been sent.'))
        self.assertRedirects(response, reverse('reman:part_check'), status_code=302)

    def test_base_ref_table(self):
        url = reverse('reman:base_ref_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(EcuRefBase, 'view_ecurefbase')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ecu_hw_table(self):
        url = reverse('reman:ecu_hw_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ecu_hw_generate_view(self):
        url = reverse('reman:ecu_hw_generate')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertRedirects(response, reverse('reman:ecu_hw_table'), status_code=302)

    def test_ecu_dump_table(self):
        url = reverse('reman:ecu_dump_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_default_table(self):
        url =reverse('reman:default_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(Default, 'view_default')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_repair_view_set_is_disconnected(self):
        response = self.client.get(reverse('reman:api_repair-list'), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.authError)

    def test_part_create_view(self):
        barcode = '9676543210'
        url = reverse('reman:part_create', kwargs={'barcode': barcode})
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(EcuModel, 'check_ecumodel')
        self.login()
        for nb in range(2):
            response = self.client.get(url + f"?next={nb}")
            if nb == 2:
                self.assertEqual(response.status_code, 404)
            else:
                self.assertEqual(response.status_code, 200)

    def test_ref_base_edit_view(self):
        url = reverse('reman:edit_ref_base', kwargs={'barcode': self.barcode})
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(EcuModel, 'change_ecumodel')
        self.login()
        for nb in range(2):
            response = self.client.get(url + f"?next={nb}")
            self.assertEqual(response.status_code, 200)

    def test_batch_pdf_generate(self):
        url = reverse('reman:batch_pdf', kwargs={'pk': self.psaBatch.pk})
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(Batch, 'pdfgen_batch')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_default(self):
        """
        Create Default through CreateView.
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

    def test_update_default(self):
        """
        Update Default throught UpdateView.
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
