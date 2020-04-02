from django.urls import reverse

from dashboard.tests.base import UnitTest

from squalaetp.models import Xelon


class XelonTestCase(UnitTest):

    def setUp(self):
        super().setUp()
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
        self.add_perms_user(Xelon, "view_xelon")
        Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                             modele_vehicule='peugeot')

    def test_xelon_table_page_is_disconnected(self):
        response = self.client.get(reverse('squalaetp:xelon'))
        self.assertRedirects(response, '/accounts/login/?next=/squalaetp/xelon/', status_code=302)

    def test_xelon_table_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('squalaetp:xelon'))
        self.assertEqual(response.status_code, 200)

    def test_xelon_edit_page_is_disconnected(self):
        response = self.client.get(reverse('squalaetp:xelon_edit', kwargs={'file_id': 1}))
        self.assertRedirects(response, '/accounts/login/?next=/squalaetp/xelon/1/edit/', status_code=302)

    def test_xelon_edit_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('squalaetp:xelon_edit', kwargs={'file_id': 1}))
        self.assertEqual(response.status_code, 200)

    # def test_xelon_detail_page_is_not_found(self):
    #     response = self.client.get(reverse('squalaetp:xelon_detail', kwargs={'file_id': 2}))
    #     self.assertEqual(response.status_code, 404)
