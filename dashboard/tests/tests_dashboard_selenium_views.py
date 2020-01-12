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
        login = driver.find_elements_by_css_selector('input.btn.btn-primary.btn-user.btn-block')
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
        login = driver.find_elements_by_css_selector('input.btn.btn-primary.btn-user.btn-block')
        username.send_keys('toto')
        password.send_keys('toto')
        login[0].click()

        self.assertEqual(driver.current_url, self.live_server_url + '/accounts/login/')

    def test_soft_add_is_valid(self):
        driver = self.driver
        old_soft = CsdSoftware.objects.count()

        # Creating session cookie for to access Software add form
        self.client.login(username='toto', password='totopassword')
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/dashboard/soft/add/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/dashboard/soft/add/')

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
        self.assertEqual(driver.current_url, self.live_server_url + '/dashboard/soft/add/')

    def test_soft_list_page(self):
        driver = self.driver
        driver.get(self.live_server_url + '/dashboard/soft/')
        self.assertEqual(driver.current_url, self.live_server_url + '/dashboard/soft/')
