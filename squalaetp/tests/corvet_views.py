from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from squalaetp.models import Corvet

User = get_user_model()


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
        response = self.client.get(reverse('squalaetp:corvet_insert'))
        self.assertEqual(response.status_code, 302)

    def test_corvet_insert_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('squalaetp:corvet_insert'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_is_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_corvets = Corvet.objects.count()
        response = self.client.post(reverse('squalaetp:corvet_insert'), {'vin': self.vin, 'xml_data': self.data})
        new_corvets = Corvet.objects.count()
        self.assertEqual(new_corvets, old_corvets + 1)
        self.assertEqual(response.status_code, 302)

    def test_corvet_insert_page_is_not_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_corvets = Corvet.objects.count()
        vin = ''
        response = self.client.post(reverse('squalaetp:corvet_insert'), {'vin': vin, 'xml_data': self.data})
        new_corvets = Corvet.objects.count()
        self.assertEqual(new_corvets, old_corvets)
        self.assertFormError(response, 'form', 'vin', _('This field is required.'))
        self.assertEqual(response.status_code, 200)

    def test_corvet_insert_page_with_vin_is_not_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_corvets = Corvet.objects.count()
        for vin in ['123456789', 'VF4ABCDEF12345678']:
            response = self.client.post(reverse('squalaetp:corvet_insert'), {'vin': vin, 'xml_data': self.data})
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
            response = self.client.post(reverse('squalaetp:corvet_insert'), {'vin': self.vin, 'xml_data': xml_data})
            new_corvets = Corvet.objects.count()
            self.assertEqual(new_corvets, old_corvets)
            self.assertFormError(
                response, 'form', 'xml_data',
                _('Invalid XML data')
            )
            self.assertEqual(response.status_code, 200)


class CorvetSeleniumTestCase(LiveServerTestCase):

    def setUp(self):
        options = Options()
        options.add_argument('-headless')
        self.driver = webdriver.Firefox(firefox_options=options)
        self.driver.implicitly_wait(30)
        super(CorvetSeleniumTestCase, self).setUp()
        User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
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

    def tearDown(self):
        self.driver.quit()
        super(CorvetSeleniumTestCase, self).tearDown()

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
        self.assertEqual(driver.current_url, self.live_server_url + '/')
