from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext as _


from squalaetp.models import Corvet
from dashboard.models import User


class CorvetTestCase(TestCase):

    def setUp(self):
        self.data = (
            '<?xml version="1.0" encoding="UTF-8"?><MESSAGE><ENTETE><EMETTEUR>CLARION_PROD</EMETTEUR></ENTETE>'
            '<VEHICULE Existe="O">'
            '<DONNEES_VEHICULE><WMI>VF3</WMI><VDS>ABCDEF</VDS><VIS>12345678</VIS>'
            '<TRANSMISSION>0R</TRANSMISSION></DONNEES_VEHICULE>'
            '<LISTE_ATTRIBUTS><ATTRIBUT>DAT24</ATTRIBUT><ATTRIBUT>GG805</ATTRIBUT></LISTE_ATTRIBUTS>'
            '<LISTE_ORGANES><ORGANE>10JBCJ3028478</ORGANE><ORGANE>20DS850837512</ORGANE></LISTE_ORGANES>'
            '<LISTE_ELECTRONIQUES><ELECTRONIQUE>14A9666571380</ELECTRONIQUE>'
            '<ELECTRONIQUE>P4A9666220599</ELECTRONIQUE></LISTE_ELECTRONIQUES>'
            '</VEHICULE></MESSAGE>'
        )
        self.vin = 'VF3ABCDEF12345678'
        User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')

    def test_corvet_table_page_is_disconnected(self):
        response = self.client.get(reverse('squalaetp:corvet'))
        self.assertEqual(response.status_code, 302)

    def test_corvet_table_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('squalaetp:corvet'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_is_disconnected(self):
        response = self.client.get(reverse('squalaetp:corvet-insert'))
        self.assertEqual(response.status_code, 302)

    def test_corvet_insert_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('squalaetp:corvet-insert'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_is_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_corvets = Corvet.objects.count()
        response = self.client.post(reverse('squalaetp:corvet-insert'), {'vin': self.vin, 'xml_data': self.data})
        new_corvets = Corvet.objects.count()
        self.assertEqual(new_corvets, old_corvets + 1)
        self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_is_not_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_corvets = Corvet.objects.count()
        vin = ''
        response = self.client.post(reverse('squalaetp:corvet-insert'), {'vin': vin, 'xml_data': self.data})
        new_corvets = Corvet.objects.count()
        self.assertEqual(new_corvets, old_corvets)
        self.assertFormError(response, 'form', 'vin', _('This field is required.'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_with_vin_is_not_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_corvets = Corvet.objects.count()
        for vin in ['123456789', 'VF4ABCDEF12345678']:
            response = self.client.post(reverse('squalaetp:corvet-insert'), {'vin': vin, 'xml_data': self.data})
            new_corvets = Corvet.objects.count()
            self.assertEqual(new_corvets, old_corvets)
            self.assertFormError(
                response, 'form', 'vin',
                _('The V.I.N. is invalid, it should be 17 characters and be part of PSA vehicles')
            )
            self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_with_xml_data_is_not_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_corvets = Corvet.objects.count()
        for xml_data in ['abcdefgh', '<?xml version="1.0" encoding="UTF-8"?>']:
            response = self.client.post(reverse('squalaetp:corvet-insert'), {'vin': self.vin, 'xml_data': xml_data})
            new_corvets = Corvet.objects.count()
            self.assertEqual(new_corvets, old_corvets)
            self.assertFormError(
                response, 'form', 'xml_data',
                _('Invalid XML data')
            )
            self.assertEqual(response.status_code, 200)

    def test_corvet_detail_page_is_disconnected(self):
        response = self.client.get(reverse('squalaetp:corvet-detail', kwargs={'vin': self.vin}))
        self.assertEqual(response.status_code, 302)

    def test_corvet_detail_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        self.client.post(reverse('squalaetp:corvet-insert'), {'vin': self.vin, 'xml_data': self.data})
        response = self.client.get(reverse('squalaetp:corvet-detail', kwargs={'vin': self.vin}))
        self.assertEqual(response.status_code, 200)

    def test_corvet_detail_page_is_not_found(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('squalaetp:corvet-detail', kwargs={'vin': "123456789"}))
        self.assertEqual(response.status_code, 404)
