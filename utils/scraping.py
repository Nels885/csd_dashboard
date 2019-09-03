import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class ScrapingCorvet(webdriver.Firefox):
    """ Scraping data Corvet of the repairnav web site"""
    START_URLS = 'https://www.repairnav.com/clarionservice_v2/corvet.xhtml'

    def __init__(self):
        """ Initialization """
        options = Options()
        options.add_argument('-headless')
        super().__init__(firefox_options=options)
        self.get(self.START_URLS)
        self.implicitly_wait(10)

    def result(self, vin_value=None):
        """
        Corvet data recovery
        :param vin_value: VIN number for the Corvet data
        :return: Corvet data
        """
        data = None
        for _ in range(2):
            self.login()
            vin = self.find_element_by_name('form:input_vin')
            submit = self.find_element_by_id('form:suite')
            if vin_value:
                vin.send_keys(vin_value)
            else:
                vin.clear()
            submit.click()
            corvet = self.find_element_by_name('form:resultat_CORVET')
            data = corvet.text
            self.logout()
        return data

    def login(self):
        """
        Login on the web site
        """
        username = self.find_element_by_name('form:identifiant2')
        password = self.find_element_by_name('form:password2')
        login = self.find_elements_by_id('form:login2')
        username.send_keys(os.environ.get('USER_CORVET'))
        password.send_keys(os.environ.get('PWD_CORVET'))
        login[0].click()

    def logout(self):
        """
        Logout on the web site
        :return:
        """
        logout = self.find_element_by_id('form:deconnect2')
        logout.click()
