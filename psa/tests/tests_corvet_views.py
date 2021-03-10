from django.urls import reverse
from django.utils.translation import ugettext as _

from dashboard.tests.base import UnitTest

from psa.models import Corvet


class CorvetTestCase(UnitTest):

    def setUp(self):
        super(CorvetTestCase, self).setUp()

    def test_corvet_insert_page(self):
        response = self.client.get(reverse('psa:corvet_insert'))
        self.assertEqual(response.status_code, 302)
        self.add_perms_user(Corvet, "add_corvet")
        self.login()
        response = self.client.get(reverse('psa:corvet_insert'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_is_valid(self):
        self.add_perms_user(Corvet, "add_corvet")
        self.login()
        old_corvets = Corvet.objects.count()
        response = self.client.post(reverse('psa:corvet_insert'), {'vin': self.vin, 'xml_data': self.xmlData})
        new_corvets = Corvet.objects.count()
        self.assertEqual(new_corvets, old_corvets + 1)
        self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_is_not_valid(self):
        self.add_perms_user(Corvet, "add_corvet")
        self.login()
        old_corvets = Corvet.objects.count()
        vin = ''
        response = self.client.post(reverse('psa:corvet_insert'), {'vin': vin, 'xml_data': self.xmlData})
        new_corvets = Corvet.objects.count()
        self.assertEqual(new_corvets, old_corvets)
        self.assertFormError(response, 'form', 'vin', _('This field is required.'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_with_vin_is_not_valid(self):
        self.add_perms_user(Corvet, "add_corvet")
        self.login()
        old_corvets = Corvet.objects.count()
        for vin in ['123456789', 'ABCDEFGH123456789']:
            response = self.client.post(reverse('psa:corvet_insert'), {'vin': vin, 'xml_data': self.xmlData})
            new_corvets = Corvet.objects.count()
            self.assertEqual(new_corvets, old_corvets)
            self.assertFormError(
                response, 'form', 'vin',
                _('The V.I.N. is invalid, it should be 17 characters and be part of PSA vehicles')
            )
            self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_with_xml_data_is_not_valid(self):
        self.add_perms_user(Corvet, "add_corvet")
        self.login()
        old_corvets = Corvet.objects.count()
        for xml_data in ['abcdefgh', '<?xml version="1.0" encoding="UTF-8"?>']:
            response = self.client.post(reverse('psa:corvet_insert'), {'vin': self.vin, 'xml_data': xml_data})
            new_corvets = Corvet.objects.count()
            self.assertEqual(new_corvets, old_corvets)
            self.assertFormError(
                response, 'form', 'xml_data',
                _('Invalid XML data')
            )
            self.assertEqual(response.status_code, 200)

    def test_corvet_detail_page(self):
        # Detail page is disconnected
        response = self.client.get(reverse('psa:corvet_detail', kwargs={'vin': self.vin}))
        self.assertEqual(response.status_code, 302)

        self.add_perms_user(Corvet, 'view_corvet', 'add_corvet')
        self.login()

        # Detail is not found
        response = self.client.get(reverse('psa:corvet_detail', kwargs={'vin': "123456789"}))
        self.assertEqual(response.status_code, 404)

        # Detail is valid
        self.client.post(reverse('psa:corvet_insert'), {'vin': self.vin, 'xml_data': self.xmlData})
        response = self.client.get(reverse('psa:corvet_detail', kwargs={'vin': self.vin}))
        self.assertEqual(response.status_code, 200)
