from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group

from raspeedi.models import Raspeedi


class RaspeediTestCase(TestCase):

    def setUp(self):
        self.form_data = {
            'ref_boitier': '1234567890', 'produit': 'RT4', 'facade': 'FF', 'type': 'NAV',
            'media': 'HDD', 'connecteur_ecran': '1',
        }
        user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        user.groups.add(Group.objects.create(name="cellule"))
        user.save()

    def test_raspeedi_table_page_is_disconnected(self):
        response = self.client.get(reverse('raspeedi:table'))
        self.assertRedirects(response, '/accounts/login/?next=/raspeedi/table/', status_code=302)

    def test_raspeedi_table_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('raspeedi:table'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page_is_disconnected(self):
        response = self.client.get(reverse('raspeedi:insert'))
        self.assertRedirects(response, '/accounts/login/?next=/raspeedi/insert/', status_code=302)

    def test_raspeedi_insert_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('raspeedi:insert'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page_is_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_raspeedi = Raspeedi.objects.count()
        response = self.client.post(reverse('raspeedi:insert'), self.form_data)
        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi + 1)
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page_is_not_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_raspeedi = Raspeedi.objects.count()
        response = self.client.post(reverse('raspeedi:insert'))
        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi)
        self.assertFormError(response, 'form', 'ref_boitier', _('This field is required.'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_edit_page_is_disconnected(self):
        Raspeedi.objects.create(**self.form_data)
        response = self.client.get(reverse('raspeedi:edit', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 302)

    def test_raspeedi_edit_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        Raspeedi.objects.create(**self.form_data)
        response = self.client.get(reverse('raspeedi:edit', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_detail_page_is_valid(self):
        Raspeedi.objects.create(**self.form_data)
        response = self.client.get(reverse('raspeedi:detail', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_detail_page_is_not_found(self):
        response = self.client.get(reverse('raspeedi:detail', kwargs={'ref_case': 1234567890}))
        self.assertEqual(response.status_code, 404)
