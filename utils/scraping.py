import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constance import config

logger = logging.getLogger('command')


class Scraping(webdriver.Chrome):
    ERROR = False

    def __init__(self):
        """ Initialization """
        options = Options()
        if config.PROXY_HOST_SCRAPING and config.PROXY_PORT_SCRAPING:
            options.add_argument(f'proxy-server={config.PROXY_HOST_SCRAPING}:{config.PROXY_PORT_SCRAPING}')
        options.add_argument('headless')
        options.add_argument("no-sandbox")  # bypass OS security model
        options.add_argument("disable-dev-shm-usage")  # overcome limited resource problems
        super().__init__(executable_path="/usr/local/bin/chromedriver", chrome_options=options)
        self.set_page_load_timeout(30)

    def close(self, **kwargs):
        try:
            if not self.ERROR:
                self.quit()
        except Exception as err:
            self._logger_error('close()', err)
        finally:
            self.ERROR = kwargs.get('error', self.ERROR)

    @staticmethod
    def _logger_error(message, err):
        exception_type = type(err).__name__
        logger.error(f"{exception_type} - {message}: {err}")


class ScrapingCorvet(Scraping):
    """ Scraping data Corvet of the repairnav website"""
    START_URLS = 'https://www.repairnav.com/clarionservice_v2/corvet.xhtml'

    def __init__(self, *args, **kwargs):
        """ Initialization """
        self.username = kwargs.get('username', config.CORVET_USER)
        self.password = kwargs.get('password', config.CORVET_PWD)
        if not kwargs.get('test', False) and self.username and self.password:
            try:
                super(ScrapingCorvet, self).__init__()
                self.get(self.START_URLS)
            except Exception as err:
                self._logger_error('__init__()', err)
                self.close(error=True)
        else:
            self.ERROR = True

    def result(self, vin_value=None):
        """
        Corvet data recovery
        :param vin_value: VIN number for the Corvet data
        :return: Corvet data
        """
        if not self.ERROR and self.login():
            try:
                WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'form:input_vin'))).clear()
                vin = self.find_element_by_name('form:input_vin')
                submit = self.find_element_by_id('form:suite')
                if vin_value:
                    vin.send_keys(vin_value)
                submit.click()
                time.sleep(1)
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
        Login on the website
        """
        try:
            WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'form:identifiant2')))
            username = self.find_element_by_name('form:identifiant2')
            password = self.find_element_by_name('form:password2')
            login = self.find_element_by_id('form:login2')
            for element, value in {username: self.username, password: self.password}.items():
                element.clear()
                element.send_keys(value)
            login.click()
        except Exception as err:
            self._logger_error('login()', err)
            self.close(error=True)
            return False
        return True

    def logout(self):
        """
        Logout on the website
        :return:
        """
        try:
            WebDriverWait(self, 10).until(EC.presence_of_element_located((By.ID, 'form:deconnect2'))).click()
        except Exception as err:
            self._logger_error('logout()', err)
            self.quit()
            return False
        return True


class ScrapingSivin(ScrapingCorvet):
    """ Scraping data SIVIN of the repairnav website"""
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
                WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'form:input_immat'))).clear()
                immat = self.find_element_by_name('form:input_immat')
                submit = self.find_element_by_id('form:suite')
                if immat_value:
                    immat.send_keys(immat_value)
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


class ScrapingPartslink24(Scraping):
    """ Scraping data Corvet of the partslink24 website"""
    START_URLS = 'https://www.partslink24.com'

    def __init__(self, *args, **kwargs):
        """ Initialization """
        self.account = kwargs.get('account', '')
        self.user = kwargs.get('user', '')
        self.password = kwargs.get('password', '')
        if not kwargs.get('test', False) and self.account and self.user and self.password:
            try:
                super(ScrapingPartslink24, self).__init__()

                self.get(self.START_URLS)
                self.privaty_settings()
            except Exception as err:
                self._logger_error('__init__()', err)
                self.close(error=True)
        else:
            self.ERROR = True

    def result(self, vin_value=None):
        """
        Corvet data recovery
        :param vin_value: VIN number for the Corvet data
        :return: Corvet data
        """
        if not self.ERROR and self.login():
            try:
                WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'form:input_vin'))).clear()
                vin = self.find_element_by_name('form:input_vin')
                submit = self.find_element_by_id('form:suite')
                if vin_value:
                    vin.send_keys(vin_value)
                submit.click()
                time.sleep(1)
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

    def privaty_settings(self):
        WebDriverWait(self, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@data-testid="uc-accept-all-button"]')))
        accept_all = self.find_element_by_xpath('//button[@data-testid="uc-accept-all-button"]')
        accept_all.click()

    def login(self):
        """
        Login on the website
        """
        try:
            WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'accountLogin')))
            account = self.find_element_by_name('accountLogin')
            user = self.find_element_by_name('userLogin')
            password = self.find_element_by_name('loginBean.password')
            for element, value in {account: self.account, user: self.user, password: self.password}.items():
                element.clear()
                element.send_keys(value)
            login = self.find_element_by_id('login-btn')
            login.click()
            if self.find_element_by_id('squeezeout-login-btn'):
                self.find_element_by_id('squeezeout-login-btn').click()
        except Exception as err:
            self._logger_error('login()', err)
            self.close(error=True)
            return False
        return True

    def logout(self):
        """
        Logout on the website
        :return:
        """
        try:
            WebDriverWait(self, 10).until(EC.presence_of_element_located((By.ID, 'logoutLink'))).click()
        except Exception as err:
            self._logger_error('logout()', err)
            self.quit()
            return False
        return True
