import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from constance import config

logger = logging.getLogger('command')

profile = webdriver.FirefoxProfile()
if config.PROXY_HOST_SCRAPING and config.PROXY_PORT_SCRAPING:
    profile.set_preference("network.proxy.http", config.PROXY_HOST_SCRAPING)
    profile.set_preference("network.proxy.http_port", config.PROXY_PORT_SCRAPING)


class ScrapingCorvet(webdriver.Firefox):
    """ Scraping data Corvet of the repairnav web site"""
    START_URLS = 'https://www.repairnav.com/clarionservice_v2/corvet.xhtml'
    ERROR = False

    def __init__(self, username, password):
        """ Initialization """
        self.username = username
        self.password = password
        options = Options()
        options.add_argument('-headless')
        try:
            super(ScrapingCorvet, self).__init__(firefox_profile=profile, firefox_options=options)
            self.implicitly_wait(10)
            self.get(self.START_URLS)
        except WebDriverException:
            self.quit()
            self.ERROR = True

    def result(self, vin_value=None):
        """
        Corvet data recovery
        :param vin_value: VIN number for the Corvet data
        :return: Corvet data
        """
        if not self.ERROR and self.login():
            try:
                vin = self.find_element_by_name('form:input_vin')
                submit = self.find_element_by_id('form:suite')
                vin.clear()
                if vin_value:
                    vin.send_keys(vin_value)
                submit.click()
                time.sleep(1)
                data = WebDriverWait(self, 10).until(
                    EC.presence_of_element_located((By.NAME, 'form:resultat_CORVET'))
                ).text
            except Exception as err:
                exception_type = type(err).__name__
                logger.error(f'{exception_type} - result(): {err}')
                data = "Exception or timeout error !"
                self.ERROR = True
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
            for element, value in {username: self.username, password: self.password}.items():
                element.clear()
                element.send_keys(value)
            login.click()
            WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'form:input_vin')))
        except Exception as err:
            exception_type = type(err).__name__
            logger.error(f"{exception_type} - login(): {err}")
            self.quit()
            self.ERROR = True
            return self.ERROR
        return True

    def logout(self):
        """
        Logout on the web site
        :return:
        """
        try:
            logout = self.find_element_by_id('form:deconnect2')
            logout.click()
        except Exception as err:
            exception_type = type(err).__name__
            logger.error(f"{exception_type} - logout(): {err}")
            self.quit()
            return False
        return True
