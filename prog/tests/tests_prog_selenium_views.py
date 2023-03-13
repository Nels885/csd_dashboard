from selenium.webdriver.support.ui import Select

from dashboard.tests.base import FunctionalTest, By
from prog.models import Raspeedi


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
        driver.get(self.live_server_url + '/prog/insert/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/prog/insert/')

        # Inserting values into the form
        ref_case = driver.find_element(By.NAME, 'ref_boitier')
        product = driver.find_element(By.NAME, 'produit')
        front = driver.find_element(By.NAME, 'facade')
        type = driver.find_element(By.NAME, 'type')
        media = driver.find_element(By.NAME, 'media')
        screen_connector = driver.find_element(By.NAME, 'connecteur_ecran')
        submit = driver.find_element(By.NAME, 'btn_raspeedi_insert')
        ref_case.send_keys('1234567890')
        product.send_keys('RT4')
        front.send_keys('FF')
        Select(type).select_by_visible_text('Navigation')
        Select(media).select_by_visible_text('Disque Dur')
        Select(screen_connector).select_by_visible_text('1')
        submit.click()

        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi + 1)
        self.assertEqual(driver.current_url, self.live_server_url + '/prog/insert/')

    def test_raspeedi_table_page(self):
        driver = self.driver

        # Creating session cookie for to access Raspeedi insert form
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/prog/table/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/prog/table/')

        self.assertEqual(driver.current_url, self.live_server_url + '/prog/table/')
