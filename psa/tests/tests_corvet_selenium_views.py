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
