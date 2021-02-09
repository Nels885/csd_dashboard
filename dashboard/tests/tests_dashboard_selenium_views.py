from dashboard.tests.base import FunctionalTest


class DashboardSeleniumTestCase(FunctionalTest):

    def setUp(self):
        super(DashboardSeleniumTestCase, self).setUp()

    def test_login_page_is_valid(self):
        driver = self.driver
        driver.get(self.live_server_url + '/accounts/login/')

        # Inserting values into the form
        username = driver.find_element_by_name('username')
        password = driver.find_element_by_name('password')
        login = driver.find_elements_by_css_selector('button.btn.btn-primary.btn-user.btn-block')
        username.send_keys('toto')
        password.send_keys('totopassword')
        login[0].click()

        self.assertEqual(driver.current_url, self.live_server_url + '/dashboard/charts/')

    def test_login_page_is_not_valid(self):
        driver = self.driver
        driver.get(self.live_server_url + '/accounts/login/')

        # Inserting values into the form
        username = driver.find_element_by_name('username')
        password = driver.find_element_by_name('password')
        login = driver.find_elements_by_css_selector('button.btn.btn-primary.btn-user.btn-block')
        username.send_keys('toto')
        password.send_keys('toto')
        login[0].click()

        self.assertEqual(driver.current_url, self.live_server_url + '/accounts/login/')
