from selenium.webdriver.support.ui import Select

from dashboard.tests.base import FunctionalTest
from raspeedi.models import Raspeedi


class RaspeediSeleniumTestCase(FunctionalTest):

    def setUp(self):
        super(RaspeediSeleniumTestCase, self).setUp()
        self.add_perms_user(Raspeedi, "view_raspeedi", "add_raspeedi")

    def test_raspeedi_insert_is_valid(self):
        driver = self.driver
        old_raspeedi = Raspeedi.objects.count()

        # Creating session cookie for to access Raspeedi insert form
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/raspeedi/insert/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/raspeedi/insert/')

        # Inserting values into the form
        ref_case = driver.find_element_by_name('ref_boitier')
        product = driver.find_element_by_name('produit')
        front = driver.find_element_by_name('facade')
        type = driver.find_element_by_name('type')
        media = driver.find_element_by_name('media')
        screen_connector = driver.find_element_by_name('connecteur_ecran')
        submit = driver.find_element_by_name('btn_raspeedi_insert')
        ref_case.send_keys('1234567890')
        product.send_keys('RT4')
        front.send_keys('FF')
        Select(type).select_by_visible_text('Navigation')
        Select(media).select_by_visible_text('Disque Dur')
        Select(screen_connector).select_by_visible_text('1')
        submit.click()

        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi + 1)
        self.assertEqual(driver.current_url, self.live_server_url + '/raspeedi/insert/')

    def test_raspeedi_table_page(self):
        driver = self.driver

        # Creating session cookie for to access Raspeedi insert form
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/raspeedi/table/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/raspeedi/table/')

        self.assertEqual(driver.current_url, self.live_server_url + '/raspeedi/table/')
