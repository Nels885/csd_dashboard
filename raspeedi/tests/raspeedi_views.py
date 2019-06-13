from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select

from raspeedi.models import Raspeedi

User = get_user_model()


class RaspeediTestCase(TestCase):

    def setUp(self):
        self.form_data = {
            'ref_boitier': '1234567890', 'produit': 'RT4', 'facade': 'FF', 'type': 'NAV',
            'media': 'HDD', 'connecteur_ecran': '1',
        }
        User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')

    def test_raspeedi_table_page(self):
        response = self.client.get(reverse('raspeedi:table'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page_is_disconnected(self):
        response = self.client.get(reverse('raspeedi:insert'))
        self.assertEqual(response.status_code, 302)

    def test_raspeedi_insert_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('raspeedi:insert'))
        self.assertEqual(response.status_code, 200)

    def test_raspeedi_insert_page_is_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_raspeedi = Raspeedi.objects.count()
        response = self.client.post(reverse('raspeedi:insert'), self.form_data)
        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi + 1)
        self.assertEqual(response.status_code, 302)

    def test_corvet_insert_page_is_not_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_raspeedi = Raspeedi.objects.count()
        response = self.client.post(reverse('raspeedi:insert'))
        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi)
        self.assertFormError(response, 'form', 'ref_boitier', 'Ce champ est obligatoire.')
        self.assertEqual(response.status_code, 200)


class RaspeediFormTestCase(LiveServerTestCase):

    def setUp(self):
        options = Options()
        options.add_argument('-headless')
        self.driver = webdriver.Firefox(firefox_options=options)
        self.driver.implicitly_wait(30)
        super(RaspeediFormTestCase, self).setUp()
        User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')

    def tearDown(self):
        self.driver.quit()
        super(RaspeediFormTestCase, self).tearDown()

    def test_raspeedi_insert(self):
        driver = self.driver
        old_raspeedi = Raspeedi.objects.count()
        self.client.login(username='toto', password='totopassword')
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/raspeedi/insert/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/raspeedi/insert/')

        ref_case = driver.find_element_by_name('ref_boitier')
        product = driver.find_element_by_name('produit')
        front = driver.find_element_by_name('facade')
        type = driver.find_element_by_name('type')
        media = driver.find_element_by_name('media')
        screen_connector = driver.find_element_by_name('connecteur_ecran')
        submit = driver.find_element_by_name('btn_insert_raspeedi')

        ref_case.send_keys('1234567890')
        product.send_keys('RT4')
        front.send_keys('FF')
        Select(type).select_by_visible_text('Navigation')
        Select(media).select_by_visible_text('Disque Dur')
        Select(screen_connector).select_by_visible_text('1')
        submit.click()

        new_raspeedi = Raspeedi.objects.count()
        self.assertEqual(new_raspeedi, old_raspeedi + 1)
        self.assertEqual(driver.current_url, self.live_server_url + '/')

    def test_raspeedi_table_page(self):
        driver = self.driver
        driver.get(self.live_server_url + '/raspeedi/table/')
        self.assertEqual(driver.current_url, self.live_server_url + '/raspeedi/table/')
