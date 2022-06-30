from django.utils.translation import gettext as _

from dashboard.tests.base import FunctionalTest


class DashboardSeleniumTestCase(FunctionalTest):

    def setUp(self):
        super(DashboardSeleniumTestCase, self).setUp()

    def test_login_page_is_valid(self):
        driver = self.driver
        driver.get(self.live_server_url + '/accounts/login/')

        # Inserting values into the form
        username = driver.find_element_by_id('id_username')
        password = driver.find_element_by_id('id_password')
        login = driver.find_elements_by_css_selector('button.btn.btn-primary.btn-user.btn-block')
        username.send_keys('toto')
        password.send_keys('totopassword')
        login[0].click()

        self.assertEqual(driver.current_url, self.live_server_url + '/dashboard/charts/')

    def test_login_page_is_not_valid(self):
        driver = self.driver
        driver.get(self.live_server_url + '/accounts/login/')

        # Inserting values into the form
        username = driver.find_element_by_id('id_username')
        password = driver.find_element_by_id('id_password')
        login = driver.find_elements_by_css_selector('button.btn.btn-primary.btn-user.btn-block')
        username.send_keys('toto')
        password.send_keys('toto')
        login[0].click()

        self.assertEqual(driver.current_url, self.live_server_url + '/accounts/login/')

    def test_logout_modal_view(self):
        driver = self.driver

        # Creating session cookie for to access Raspeedi insert form
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url)
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()

        # User clicks logout button
        driver.find_element_by_id('logout-nav-btn').click()

        #logout modal opens
        modal = self.wait_for(element_id='modal')
        modal.find_element_by_css_selector('a.btn.btn-primary').click()

        # The user is redirected to the homepage
        self.assertEqual(driver.current_url, self.live_server_url + "/")
