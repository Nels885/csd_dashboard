from dashboard.tests.base import FunctionalTest
from squalaetp.models import Corvet


class CorvetSeleniumTestCase(FunctionalTest):

    def setUp(self):
        super(CorvetSeleniumTestCase, self).setUp()
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
        self.add_group_user("cellule")

    def test_corvet_table_page_is_connected(self):
        driver = self.driver

        # Creating session cookie for to access Raspeedi insert form
        self.client.login(username='toto', password='totopassword')
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/squalaetp/corvet/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/squalaetp/corvet/')

        self.assertEqual(driver.current_url, self.live_server_url + '/squalaetp/corvet/')

    def test_corvet_insert_is_valid(self):
        driver = self.driver
        old_corvet = Corvet.objects.count()

        # Creating session cookie for to access Raspeedi insert form
        self.client.login(username='toto', password='totopassword')
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/squalaetp/corvet/insert/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/squalaetp/corvet/insert/')

        # Inserting values into the form
        vin = driver.find_element_by_name('vin')
        xml_data = driver.find_element_by_name('xml_data')
        submit = driver.find_element_by_name('btn_corvet_insert')
        vin.send_keys(self.vin)
        xml_data.send_keys(self.data)
        submit.click()

        new_corvet = Corvet.objects.count()
        self.assertEqual(new_corvet, old_corvet + 1)
        self.assertEqual(driver.current_url, self.live_server_url + '/squalaetp/corvet/insert/')
