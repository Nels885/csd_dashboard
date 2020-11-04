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
        xelon = Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                                     modele_vehicule='peugeot')
        self.xelonId = str(xelon.id)

    def test_xelon_table_page(self):
        response = self.client.get(reverse('squalaetp:xelon'))
        self.assertRedirects(response, '/accounts/login/?next=/squalaetp/xelon/', status_code=302)
        self.login()
        response = self.client.get(reverse('squalaetp:xelon'))
        self.assertEqual(response.status_code, 200)

    def test_xelon_edit_page(self):
        response = self.client.get(reverse('squalaetp:xelon_edit', kwargs={'file_id': self.xelonId}))
        self.assertRedirects(
            response, '/accounts/login/?next=/squalaetp/xelon/' + self.xelonId + '/edit/', status_code=302)
        self.login()
        response = self.client.get(reverse('squalaetp:xelon_edit', kwargs={'file_id': self.xelonId}))
        self.assertEqual(response.status_code, 200)

    def test_xelon_detail_page(self):
        response = self.client.get(reverse('squalaetp:detail', kwargs={'file_id': self.xelonId}))
        self.assertRedirects(response, '/accounts/login/?next=/squalaetp/' + self.xelonId + '/detail/', status_code=302)

        # Detail is not found
        self.login()
        response = self.client.get(reverse('squalaetp:detail', kwargs={'file_id': 666}))
        self.assertEqual(response.status_code, 404)

        # Detail is valid
        response = self.client.get(reverse('squalaetp:detail', kwargs={'file_id': self.xelonId}))
        self.assertEqual(response.status_code, 200)

    def test_stock_table_page(self):
        response = self.client.get(reverse('squalaetp:stock_parts'))
        self.assertRedirects(response, '/accounts/login/?next=/squalaetp/stock-parts/', status_code=302)
        self.login()
        response = self.client.get(reverse('squalaetp:stock_parts'))
        self.assertEqual(response.status_code, 200)
