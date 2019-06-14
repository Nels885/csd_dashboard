from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from django.utils import translation
from django.contrib.auth import get_user_model

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

User = get_user_model()


class DashboardTestCase(TestCase):

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')

    def test_set_language_vue_is_valid(self):
        for lang in ['fr', 'en']:
            response = self.client.get(reverse('dashboard:set_lang', args={'user_language': lang}))
            self.assertTrue(translation.check_for_language(lang))
            self.assertEqual(response.status_code, 302)


class DashboardSeleniumTestCase(LiveServerTestCase):

    def setUp(self):
        options = Options()
        options.add_argument('-headless')
        self.driver = webdriver.Firefox(firefox_options=options)
        self.driver.implicitly_wait(30)
        super(DashboardSeleniumTestCase, self).setUp()
        User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')

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

        self.assertEqual(driver.current_url, self.live_server_url + '/')

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

