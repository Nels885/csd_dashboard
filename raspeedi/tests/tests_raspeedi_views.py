from django.urls import reverse
from django.utils.translation import ugettext as _

from dashboard.tests.base import UnitTest

from raspeedi.models import Raspeedi, UnlockProduct
from squalaetp.models import Xelon


class RaspeediTestCase(UnitTest):

    def setUp(self):
        super(RaspeediTestCase, self).setUp()
        self.form_data = {
            'ref_boitier': '1234567890', 'produit': 'RT4', 'facade': 'FF', 'type': 'NAV',
            'media': 'HDD', 'connecteur_ecran': '1',
        }
        self.add_perms_user(UnlockProduct, 'add_unlockproduct', 'view_unlockproduct')
        self.add_perms_user(Raspeedi, 'add_raspeedi', 'view_raspeedi', 'change_raspeedi')

    def test_raspeedi_table_page(self):
        response = self.client.get(reverse('raspeedi:table'))
        self.assertRedirects(response, '/accounts/login/?next=/raspeedi/table/', status_code=302)
        self.login()
        response = self.client.get(reverse('raspeedi:table'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page(self):
        response = self.client.get(reverse('raspeedi:insert'))
        self.assertRedirects(response, '/accounts/login/?next=/raspeedi/insert/', status_code=302)
        self.login()
        response = self.client.get(reverse('raspeedi:insert'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page_is_valid(self):
        self.login()
        old_raspeedi = Raspeedi.objects.count()
        response = self.client.post(reverse('raspeedi:insert'), self.form_data)
        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi + 1)
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page_is_not_valid(self):
        self.login()
        old_raspeedi = Raspeedi.objects.count()
        response = self.client.post(reverse('raspeedi:insert'))
        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi)
        # self.assertFormError(response, 'form', 'ref_boitier', _('This field is required.'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_edit_page(self):
        Raspeedi.objects.create(**self.form_data)
        response = self.client.get(reverse('raspeedi:edit', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 302)
        self.login()
        response = self.client.get(reverse('raspeedi:edit', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_detail_page(self):
        self.login()
        # Detail page is not found
        response = self.client.get(reverse('raspeedi:detail', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 404)

        # Detail page is valid
        Raspeedi.objects.create(**self.form_data)
        response = self.client.get(reverse('raspeedi:detail', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 200)

    def test_unlock_page(self):
        response = self.client.get(reverse('raspeedi:unlock_prods'))
        self.assertRedirects(response, '/accounts/login/?next=/raspeedi/unlock/', status_code=302)
        self.login()
        response = self.client.get(reverse('raspeedi:unlock_prods'))
        self.assertEqual(response.status_code, 200)

    def test_unlock_add_page_is_not_valid(self):
        self.login()
        old_unlock = UnlockProduct.objects.count()
        for xelon, message in {'azerty': 'Xelon number is invalid', 'A987654321': 'Xelon number no exist'}.items():
            response = self.client.post(reverse('raspeedi:unlock_prods'), {'unlock': xelon})
            new_unlock = UnlockProduct.objects.count()
            self.assertEqual(new_unlock, old_unlock)
            self.assertFormError(response, 'form', 'unlock', _(message))
            self.assertEqual(response.status_code, 200)

    def test_unlock_add_page_is_valid(self):
        self.login()
        Xelon.objects.create(numero_de_dossier='A123456789', vin='VF3ABCDEF12345678', modele_produit='produit',
                             modele_vehicule='peugeot')
        old_unlock = UnlockProduct.objects.count()
        response = self.client.post(reverse('raspeedi:unlock_prods'), {'unlock': 'A123456789'})
        new_unlock = UnlockProduct.objects.count()
        self.assertEqual(new_unlock, old_unlock + 1)
        self.assertEqual(response.status_code, 200)

    def test_unlock_table_page(self):
        response = self.client.get(reverse('raspeedi:unlock_table'))
        self.assertRedirects(response, '/accounts/login/?next=/raspeedi/unlock/table/', status_code=302)
        self.add_perms_user(UnlockProduct, 'view_unlockproduct')
        self.login()
        response = self.client.get(reverse('raspeedi:unlock_table'))
        self.assertEqual(response.status_code, 200)
