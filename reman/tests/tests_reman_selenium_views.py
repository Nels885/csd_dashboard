from dashboard.tests.base import FunctionalTest

from reman.models import EcuModel


class RemanSeleniumTestCase(FunctionalTest):

    def setUp(self):
        super(RemanSeleniumTestCase, self).setUp()

    def test_check_part_is_connected(self):
        driver = self.driver

        # Creating session cookie for to access Raspeedi insert form
        self.add_perms_user(EcuModel, 'check_ecumodel')
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/reman/part/check/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/reman/part/check/')

        self.assertEqual(driver.current_url, self.live_server_url + '/reman/part/check/')

    def test_check_part_is_valid(self):
        driver = self.driver

        # Creating session cookie for to access Check part form
        self.add_perms_user(EcuModel, 'check_ecumodel')
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/reman/part/check/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/reman/part/check/')

        # Inserting values into the form
        barcode = driver.find_element_by_name('barcode')
        submit = driver.find_elements_by_css_selector('button.btn.btn-success.btn-icon-split')
        barcode.send_keys('9887654321')
        submit[0].click()

        self.assertEqual(driver.current_url, self.live_server_url + '/reman/part/9887654321/create/')
