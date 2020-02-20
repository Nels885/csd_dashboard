import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from dashboard.models import UserProfile

MAX_WAIT = 10


class FunctionalTest(StaticLiveServerTestCase):

    # Basic setUp & tearDown
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def wait_for_text_in_body(self, *args, not_in=None):
        start_time = time.time()
        # Infinite loop
        while True:
            try:
                body = self.browser.find_element_by_tag_name('body')
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
                modal = self.browser.find_element_by_id(modalID)
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
                table = self.browser.find_element_by_tag_name('table')
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


class UnitTest(TestCase):

    def setUp(self):
        self.vin = 'VF3ABCDEF12345678'
        self.form_user = {'username': 'test', 'email': 'test@test.com'}
        admin = User.objects.create_user(username='admin', email='admin@admin.com', password='adminpassword')
        admin.is_staff = True
        admin.save()
        user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        user.save()
        UserProfile(user=user).save()
        self.redirectUrl = reverse('index')

    def login(self, user='user'):
        if user == 'admin':
            self.client.login(username='admin', password='adminpassword')
        else:
            self.client.login(username='toto', password='totopassword')
