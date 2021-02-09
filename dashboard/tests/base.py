import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options

MAX_WAIT = 10


class BaseTest:

    def __init__(self):
        self.vin = 'VF3ABCDEF12345678'
        self.xmlData = (
            '<?xml version="1.0" encoding="UTF-8"?><MESSAGE><ENTETE><EMETTEUR>CLARION_PROD</EMETTEUR></ENTETE>'
            '<VEHICULE Existe="O">'
            '<DONNEES_VEHICULE><WMI>VF3</WMI><VDS>ABCDEF</VDS><VIS>12345678</VIS>'
            '<TRANSMISSION>0R</TRANSMISSION></DONNEES_VEHICULE>'
            '<LISTE_ATTRIBUTS><ATTRIBUT>DAT24</ATTRIBUT><ATTRIBUT>GG805</ATTRIBUT></LISTE_ATTRIBUTS>'
            '<LISTE_ORGANES><ORGANE>10JBCJ3028478</ORGANE><ORGANE>20DS850837512</ORGANE></LISTE_ORGANES>'
            '<LISTE_ELECTRONIQUES><ELECTRONIQUE>14A9666571380</ELECTRONIQUE>'
            '<ELECTRONIQUE>P4A9666220599</ELECTRONIQUE></LISTE_ELECTRONIQUES>'
            '</VEHICULE></MESSAGE>'
        )
        self.formUser = {'username': 'test', 'email': 'test@test.com'}
        admin = User.objects.create_user(username='admin', email='admin@admin.com', password='adminpassword')
        admin.is_staff = True
        admin.save()
        self.user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        self.user.save()
        self.redirectUrl = reverse('index')
        self.nextLoginUrl = '/accounts/login/?next='

    def add_group_user(self, *args):
        for group in args:
            self.user.groups.add(Group.objects.create(name=group))

    def add_perms_user(self, model, *args):
        content_type = ContentType.objects.get_for_model(model)
        for codename in args:
            self.user.user_permissions.add(Permission.objects.get(codename=codename, content_type=content_type))


class UnitTest(TestCase, BaseTest):

    def setUp(self):
        BaseTest.__init__(self)
        TestCase.setUp(self)

    def login(self, user='user'):
        if user == 'admin':
            self.client.login(username='admin', password='adminpassword')
        else:
            self.client.login(username='toto', password='totopassword')


class FunctionalTest(StaticLiveServerTestCase, BaseTest):

    # Basic setUp & tearDown
    def setUp(self):
        options = Options()
        options.add_argument('-headless')
        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.proxy.no_proxies_on", "localhost, 127.0.0.1")
        self.driver = webdriver.Firefox(firefox_profile=profile, firefox_options=options)
        self.driver.implicitly_wait(30)
        StaticLiveServerTestCase.setUp(self)
        BaseTest.__init__(self)

    def tearDown(self):
        self.driver.quit()
        super(FunctionalTest, self).tearDown()

    def login(self, user='user'):
        if user == 'admin':
            self.client.login(username='admin', password='adminpassword')
        else:
            self.client.login(username='toto', password='totopassword')

    def wait_for_text_in_body(self, *args, not_in=None):
        start_time = time.time()
        # Infinite loop
        while True:
            try:
                body = self.driver.find_element_by_tag_name('body')
                body_text = body.text
                # Check that text is in body
                if not not_in:
                    for arg in args:
                        self.assertIn(arg, body_text)
                # Check there is no text in body
                else:
                    for arg in args:
                        self.assertNotIn(arg, body_text)
                return
            except (AssertionError, WebDriverException) as e:
                # Return exception if more than 10s pass
                if time.time() - start_time > MAX_WAIT:
                    raise e
                # Wait for 0.5s and retry
                time.sleep(0.5)

    def wait_for_modal(self, modalID):
        start_time = time.time()
        # Infinite loop
        while True:
            try:
                modal = self.driver.find_element_by_id(modalID)
                return modal
            except (AssertionError, WebDriverException) as e:
                # Return exception if more than 10s pass
                if time.time() - start_time > MAX_WAIT:
                    raise e
                # Wait for 0.5s and retry
                time.sleep(0.5)

    def wait_for_table_rows(self):
        start_time = time.time()
        # Infinite loop
        while True:
            try:
                table = self.driver.find_element_by_tag_name('table')
                tbody = table.find_element_by_tag_name('tbody')
                # Slice removes tr in thead
                trs = tbody.find_elements_by_tag_name('tr')
                return trs
            except (AssertionError, WebDriverException) as e:
                # Return exception if more than 10s pass
                if time.time() - start_time > MAX_WAIT:
                    raise e
                # Wait for 0.5s and retry
                time.sleep(0.5)

    def check_table_row(self, table_row, cells_count, cells_values):
        cells = table_row.find_elements_by_tag_name('td')
        # Compare cells count in table row with expected value
        self.assertEqual(len(cells), cells_count)
        # Compare content of cells in table row with expected values
        for i in range(len(cells_values)):
            if cells_values[i] is not None:
                self.assertEqual(cells[i].text, cells_values[i])
