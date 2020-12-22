from django.urls import reverse

from dashboard.tests.base import UnitTest

from squalaetp.models import Xelon


class XelonTestCase(UnitTest):

    def setUp(self):
        super(XelonTestCase, self).setUp()
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
        url = reverse('squalaetp:xelon')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_squalaetp_detail_page(self):
        url = reverse('squalaetp:detail', kwargs={'pk': self.xelonId})
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        # Detail is not found
        self.login()
        response = self.client.get(reverse('squalaetp:detail', kwargs={'pk': 666}))
        self.assertEqual(response.status_code, 404)

        # Detail is valid
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_stock_table_page(self):
        url = reverse('squalaetp:stock_parts')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


