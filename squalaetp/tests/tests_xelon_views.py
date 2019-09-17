from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

from squalaetp.models import Xelon


class XelonTestCase(TestCase):

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
        user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        user.groups.add(Group.objects.create(name="cellule"))
        user.save()
        Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                             modele_vehicule='peugeot')

    def test_xelon_table_page(self):
        response = self.client.get(reverse('squalaetp:xelon'))
        self.assertEqual(response.status_code, 200)

    def test_xelon_edit_page_is_disconnected(self):
        response = self.client.get(reverse('squalaetp:xelon-edit', kwargs={'file_id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_xelon_edit_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('squalaetp:xelon-edit', kwargs={'file_id': 1}))
        self.assertEqual(response.status_code, 200)

    # def test_xelon_detail_page_is_not_found(self):
    #     response = self.client.get(reverse('squalaetp:xelon-detail', kwargs={'file_id': 2}))
    #     self.assertEqual(response.status_code, 404)
