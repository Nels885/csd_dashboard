from django.urls import reverse
from django.utils.translation import gettext as _

from dashboard.tests.base import UnitTest

from prog.models import Raspeedi, UnlockProduct, ToolStatus, AET, MbedFirmware
from squalaetp.models import Xelon


class ProgTestCase(UnitTest):

    def setUp(self):
        super(ProgTestCase, self).setUp()
        self.form_data = {
            'ref_boitier': '1234567890', 'produit': 'RT4', 'facade': 'FF', 'type': 'NAV',
            'media': 'HDD', 'connecteur_ecran': '1',
        }
        self.aet_data = {
            'name': 'AET-test', 'raspi_url': '10.56.0.0', 'mbed_list': 'DIGITAL_IN;ANALOG_IN;DIGITAL_POT',
        }
        self.add_perms_user(UnlockProduct, 'add_unlockproduct', 'view_unlockproduct')
        self.add_perms_user(Raspeedi, 'add_raspeedi', 'view_raspeedi', 'change_raspeedi')
        self.add_perms_user(AET, 'add_aet', 'change_aet')
        self.tools = ToolStatus.objects.create(name="test", url="http://test.test")

    def test_raspeedi_table_page(self):
        response = self.client.get(reverse('prog:table'))
        self.assertRedirects(response, '/accounts/login/?next=/prog/table/', status_code=302)
        self.login()
        response = self.client.get(reverse('prog:table'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page(self):
        response = self.client.get(reverse('prog:insert'))
        self.assertRedirects(response, '/accounts/login/?next=/prog/insert/', status_code=302)
        self.login()
        response = self.client.get(reverse('prog:insert'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page_is_valid(self):
        self.login()
        old_raspeedi = Raspeedi.objects.count()
        response = self.client.post(reverse('prog:insert'), self.form_data)
        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi + 1)
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page_is_not_valid(self):
        self.login()
        old_raspeedi = Raspeedi.objects.count()
        response = self.client.post(reverse('prog:insert'))
        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi)
        # self.assertFormError(response, 'form', 'ref_boitier', _('This field is required.'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_edit_page(self):
        Raspeedi.objects.create(**self.form_data)
        response = self.client.get(reverse('prog:edit', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 302)
        self.login()
        response = self.client.get(reverse('prog:edit', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_detail_page(self):
        self.login()
        # Detail page is not found
        response = self.client.get(reverse('prog:detail', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 404)

        # Detail page is valid
        Raspeedi.objects.create(**self.form_data)
        response = self.client.get(reverse('prog:detail', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 200)

    def test_unlock_page(self):
        response = self.client.get(reverse('prog:unlock_prods'))
        self.assertRedirects(response, '/accounts/login/?next=/prog/unlock/', status_code=302)
        self.login()
        response = self.client.get(reverse('prog:unlock_prods'))
        self.assertEqual(response.status_code, 200)

    def test_unlock_add_page_is_not_valid(self):
        self.login()
        old_unlock = UnlockProduct.objects.count()
        for xelon, message in {'azerty': 'Xelon number is invalid', 'A987654321': 'Xelon number no exist'}.items():
            response = self.client.post(reverse('prog:unlock_prods'), {'unlock': xelon})
            new_unlock = UnlockProduct.objects.count()
            self.assertEqual(new_unlock, old_unlock)
            self.assertFormError(response, 'form', 'unlock', _(message))
            self.assertEqual(response.status_code, 200)

    def test_unlock_add_page_is_valid(self):
        self.login()
        Xelon.objects.create(numero_de_dossier='A123456789', vin='VF3ABCDEF12345678', modele_produit='produit',
                             modele_vehicule='peugeot')
        old_unlock = UnlockProduct.objects.count()
        response = self.client.post(reverse('prog:unlock_prods'), {'unlock': 'A123456789'})
        new_unlock = UnlockProduct.objects.count()
        self.assertEqual(new_unlock, old_unlock + 1)
        self.assertEqual(response.status_code, 200)

    def test_unlock_table_page(self):
        response = self.client.get(reverse('prog:unlock_table'))
        self.assertRedirects(response, '/accounts/login/?next=/prog/unlock/table/', status_code=302)
        self.add_perms_user(UnlockProduct, 'view_unlockproduct')
        self.login()
        response = self.client.get(reverse('prog:unlock_table'))
        self.assertEqual(response.status_code, 200)

    def test_tool_status_page(self):
        url = reverse('prog:tool_status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ajax_tool_status_page(self):
        for pk in [self.tools.pk, 999]:
            url = reverse('prog:ajax_tool_status', kwargs={'pk': pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(
                response.content, {'pk': pk, 'xelon': '', 'status': 'Hors ligne', 'version': '', 'status_code': 404})

    def test_ajax_tool_system_page(self):
        for pk in [self.tools.pk, 999]:
            url = reverse('prog:ajax_tool_system', kwargs={'pk': pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(
                response.content, {'pk': pk, 'msg': 'No response', 'status': 'off', 'status_code': 404})

    def test_tool_info_page(self):
        url = reverse('prog:tool_info')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        # Test if connected with permissions
        self.add_perms_user(ToolStatus, 'view_info_tools')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_aet_info_page(self):
        url = reverse('prog:aet_info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
