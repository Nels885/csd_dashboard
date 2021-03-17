from selenium.webdriver.support.ui import Select

from dashboard.tests.base import FunctionalTest
from tools.models import CsdSoftware


class ToolsSeleniumTestCase(FunctionalTest):

    def setUp(self):
        super(ToolsSeleniumTestCase, self).setUp()
        self.add_perms_user(CsdSoftware, 'add_csdsoftware')

    def test_soft_add_is_valid(self):
        driver = self.driver
        old_soft = CsdSoftware.objects.count()

        # Creating session cookie for to access Software add form
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/tools/soft/add/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/tools/soft/add/')

        # Inserting values into the form
        jig = driver.find_element_by_name('jig')
        version = driver.find_element_by_name('new_version')
        link = driver.find_element_by_name('link_download')
        status = driver.find_element_by_name('status')
        submit = driver.find_element_by_name('btn_soft_add')
        jig.send_keys('1234567890')
        version.send_keys('RT4')
        link.send_keys('FF')
        Select(status).select_by_visible_text('En test')
        submit.click()

        new_soft = CsdSoftware.objects.count()
        self.assertEqual(new_soft, old_soft + 1)
        self.assertEqual(driver.current_url, self.live_server_url + '/tools/soft/')

    def test_soft_list_page(self):
        driver = self.driver

        # Creating session cookie for to access Software add form
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/tools/soft/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/tools/soft/')

        self.assertEqual(driver.current_url, self.live_server_url + '/tools/soft/')
