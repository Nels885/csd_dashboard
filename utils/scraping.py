import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constance import config

logger = logging.getLogger('command')


class ScrapingCorvet(webdriver.Chrome):
    """ Scraping data Corvet of the repairnav web site"""
    START_URLS = 'https://www.repairnav.com/clarionservice_v2/corvet.xhtml'
    ERROR = False

    def __init__(self, username=config.CORVET_USER, password=config.CORVET_PWD):
        """ Initialization """
        self.username = username
        self.password = password
        try:
            options = Options()
            if config.PROXY_HOST_SCRAPING and config.PROXY_PORT_SCRAPING:
                options.add_argument(f'--proxy-server={config.PROXY_HOST_SCRAPING}:{config.PROXY_PORT_SCRAPING}')
            super().__init__(executable_path="/usr/local/bin/chromedriver", chrome_options=options)
            self.implicitly_wait(10)
            self.set_page_load_timeout(30)
            self.get(self.START_URLS)
        except Exception as err:
            self._logger_error('__init__()', err)
            self.close(error=True)

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
                data = WebDriverWait(self, 10).until(
                    EC.presence_of_element_located((By.NAME, 'form:resultat_CORVET'))
                ).text
                if data and len(data) == 0:
                    data = "ERREUR COMMUNICATION SYSTEME CORVET"
            except Exception as err:
                self._logger_error('CORVET result()', err)
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
            self._logger_error('login()', err)
            self.close(error=True)
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
        except Exception as err:
            self._logger_error('logout()', err)
            self.quit()
            return False
        return True

    def close(self, **kwargs):
        self.ERROR = kwargs.get('error', self.ERROR)
        try:
            if not self.ERROR:
                self.quit()
        except Exception as err:
            self._logger_error('close()', err)

    @staticmethod
    def _logger_error(message, err):
        exception_type = type(err).__name__
        logger.error(f"{exception_type} - {message}: {err}")


class ScrapingSivin(ScrapingCorvet):
    """ Scraping data SIVIN of the repairnav web site"""
    SIVIN_URLS = 'https://www.repairnav.com/clarionservice_v2/sivin.xhtml'

    def result(self, immat_value=None):
        """
        SIVIN data recovery
        :param immat_value: Immat number for the SIVIN data
        :return: SIVIN data
        """
        if not self.ERROR and self.login():
            try:
                self.get(self.SIVIN_URLS)
                vin = self.find_element_by_name('form:input_immat')
                submit = self.find_element_by_id('form:suite')
                vin.clear()
                if immat_value:
                    vin.send_keys(immat_value)
                submit.click()
                time.sleep(1)
                data = WebDriverWait(self, 10).until(
                    EC.presence_of_element_located((By.NAME, 'form:resultat_SIVIN'))
                ).text
                if data and len(data) == 0:
                    data = "ERREUR COMMUNICATION SYSTEME SIVIN"
            except Exception as err:
                self._logger_error('SIVIN result()', err)
                data = "Exception or timeout error !"
                self.ERROR = True
            self.logout()
            self.get(self.START_URLS)
        else:
            data = "Corvet login Error !!!"
        return data
