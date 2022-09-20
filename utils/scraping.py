import time
import logging
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constance import config

logger = logging.getLogger('command')


class Scraping(webdriver.Chrome):
    ERROR = False
    STATUS = None

    def __init__(self, **kwargs):
        """ Initialization """
        options = Options()
        if config.PROXY_HOST_SCRAPING and config.PROXY_PORT_SCRAPING:
            options.add_argument(f'proxy-server={config.PROXY_HOST_SCRAPING}:{config.PROXY_PORT_SCRAPING}')
        if kwargs.get('headless', True):
            options.add_argument('headless')
        options.add_argument("no-sandbox")  # bypass OS security model
        options.add_argument("disable-dev-shm-usage")  # overcome limited resource problems
        super().__init__(executable_path="/usr/local/bin/chromedriver", chrome_options=options)
        self.set_page_load_timeout(30)
        self.STATUS = "INIT"

    def is_element_exist(self, by, value):
        try:
            WebDriverWait(self, 2).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            return False
        return True

    def is_element_clicked(self, by, value):
        try:
            WebDriverWait(self, 2).until(EC.element_to_be_clickable((by, value))).click()
        except TimeoutException:
            return False
        return True

    def close(self):
        try:
            if self.STATUS not in ["QUIT", "CLOSE"]:
                super().close()
                self.STATUS = "CLOSE"
        except Exception as err:
            self._logger_error('close()', err)

    def quit(self, **kwargs):
        try:
            if self.STATUS != "QUIT":
                super().quit()
                self.STATUS = "QUIT"
        except Exception as err:
            self._logger_error('quit()', err)
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
                super(ScrapingCorvet, self).__init__(**kwargs)
                self.get(self.START_URLS)
            except Exception as err:
                self._logger_error('__init__()', err)
                self.quit(error=True)
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
            self.quit(error=True)
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
            self.quit(error=True)
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
        self.account = kwargs.get('account', config.PL24_ACCOUNT)
        self.user = kwargs.get('user', config.PL24_USER)
        self.password = kwargs.get('password', config.PL24_PWD)
        if not kwargs.get('test', False) and self.account and self.user and self.password:
            try:
                super(ScrapingPartslink24, self).__init__(**kwargs)

                self.get(self.START_URLS)
                self.privaty_settings()
            except Exception as err:
                self._logger_error('__init__()', err)
                self.quit(error=True)
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
        WebDriverWait(self, 10).until(EC.presence_of_element_located((By.ID, 'usercentrics-root')))
        shadow_host = self.find_element_by_id('usercentrics-root')
        script = 'return arguments[0].shadowRoot'
        shadow_root_dict = self.execute_script(script, shadow_host)
        id = shadow_root_dict['shadow-6066-11e4-a52e-4f735466cecf']
        shadow_root = WebElement(self, id, w3c=True)
        WebDriverWait(shadow_root, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="uc-accept-all-button"]')))
        shadow_root.find_element_by_css_selector('[data-testid="uc-accept-all-button"]').click()

    def login(self):
        """
        Login on the website
        """
        try:
            if self.STATUS in ["INIT", "LOGOUT"]:
                WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'accountLogin')))
                account = self.find_element_by_name('accountLogin')
                user = self.find_element_by_name('userLogin')
                password = self.find_element_by_name('loginBean.password')
                for element, value in {account: self.account, user: self.user, password: self.password}.items():
                    element.clear()
                    element.send_keys(value)
                WebDriverWait(self, 10).until(EC.element_to_be_clickable((By.ID, 'login-btn'))).click()
                self.is_element_clicked(By.ID, 'squeezeout-login-btn')
                if not self.is_element_exist(By.ID, 'logoutLink'):
                    return False
                self.STATUS = "LOGIN"
                return True
        except Exception as err:
            self._logger_error('login()', err)
            self.quit(error=True)
        return False

    def logout(self):
        """
        Logout on the website
        :return:
        """
        try:
            if self.STATUS == "LOGIN":
                WebDriverWait(self, 10).until(EC.presence_of_element_located((By.ID, 'logoutLink'))).click()
                self.STATUS = "LOGOUT"
                return True
        except Exception as err:
            self._logger_error('logout()', err)
            self.quit(error=True)
        return False
