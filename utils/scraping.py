import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException


class ScrapingCorvet(webdriver.Firefox):
    """ Scraping data Corvet of the repairnav web site"""
    START_URLS = 'https://www.repairnav.com/clarionservice_v2/corvet.xhtml'
    USER_CORVET = os.environ.get('USER_CORVET')
    PWD_CORVET = os.environ.get('PWD_CORVET')

    def __init__(self):
        """ Initialization """
        options = Options()
        options.add_argument('-headless')
        super().__init__(firefox_options=options)
        self.implicitly_wait(10)
        self.get(self.START_URLS)

    def result(self, vin_value=None):
        """
        Corvet data recovery
        :param vin_value: VIN number for the Corvet data
        :return: Corvet data
        """
        if self.login():
            vin = self.find_element_by_name('form:input_vin')
            submit = self.find_element_by_id('form:suite')
            vin.clear()
            if vin_value:
                vin.send_keys(vin_value)
            submit.click()
            time.sleep(3)
            data = WebDriverWait(self, 10).until(
                EC.presence_of_element_located((By.NAME, 'form:resultat_CORVET'))
            ).text
            self.logout()
        else:
            data = "Corvet login Error !!!"
        return data

    def login(self):
        """
        Login on the web site
        """
        try:
            username = self.find_element_by_name('form:identifiant2')
            password = self.find_element_by_name('form:password2')
            login = self.find_element_by_id('form:login2')
            for element, value in {username: self.USER_CORVET, password: self.PWD_CORVET}.items():
                element.clear()
                element.send_keys(value)
            login.click()
            WebDriverWait(self, 1).until(EC.presence_of_element_located((By.NAME, 'form:input_vin')))
        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
            return False
        return True

    def logout(self):
        """
        Logout on the web site
        :return:
        """
        try:
            logout = self.find_element_by_id('form:deconnect2')
            logout.click()
        except (NoSuchElementException, ElementClickInterceptedException):
            return False
        return True
