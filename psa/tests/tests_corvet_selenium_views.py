from dashboard.tests.base import FunctionalTest
from psa.models import Corvet


class CorvetSeleniumTestCase(FunctionalTest):

    def setUp(self):
        super(CorvetSeleniumTestCase, self).setUp()

    def test_corvet_table_page_is_connected(self):
        driver = self.driver

        # Creating session cookie for to access Raspeedi insert form
        self.add_perms_user(Corvet, "view_corvet")
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/psa/corvet/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/psa/corvet/')

        self.assertEqual(driver.current_url, self.live_server_url + '/psa/corvet/')

    def test_corvet_insert_is_valid(self):
        driver = self.driver
        old_corvet = Corvet.objects.count()

        # Creating session cookie for to access Raspeedi insert form
        self.add_perms_user(Corvet, "add_corvet")
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/psa/corvet/insert/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/psa/corvet/insert/')

        # Inserting values into the form
        vin = driver.find_element_by_name('vin')
        xml_data = driver.find_element_by_name('xml_data')
        submit = driver.find_element_by_name('btn_corvet_insert')
        vin.send_keys(self.vin)
        xml_data.send_keys(self.xmlData)
        submit.click()

        new_corvet = Corvet.objects.count()
        self.assertEqual(new_corvet, old_corvet + 1)
        self.assertEqual(driver.current_url, self.live_server_url + '/psa/corvet/insert/')
