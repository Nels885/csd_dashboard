from django.test import LiveServerTestCase
from django.contrib.auth.models import User, Group

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select

from dashboard.models import CsdSoftware


class DashboardSeleniumTestCase(LiveServerTestCase):

    def setUp(self):
        options = Options()
        options.add_argument('-headless')
        self.driver = webdriver.Firefox(firefox_options=options)
        self.driver.implicitly_wait(30)
        super(DashboardSeleniumTestCase, self).setUp()
        user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        user.groups.add(Group.objects.create(name="cellule"))
        user.save()

    def tearDown(self):
        self.driver.quit()
        super(DashboardSeleniumTestCase, self).tearDown()

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

        self.assertEqual(driver.current_url, self.live_server_url + '/dashboard/profile/')

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
