import time
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from django.utils.timezone import make_aware

from webdriver_manager.chrome import ChromeDriverManager
# from selenium import webdriver
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from selenium.webdriver.common.by import By
# from selenium.webdriver import ChromeOptions as Options
# from selenium.webdriver.remote.webelement import WebElement
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
from seleniumwire.webdriver import ChromeOptions as Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constance import config


logger = logging.getLogger('command')


options_seleniumWire = {
    'proxy': {
        'https': f'{config.PROXY_HOST_SCRAPING}:{config.PROXY_PORT_SCRAPING}',
        'http': f'{config.PROXY_HOST_SCRAPING}:{config.PROXY_PORT_SCRAPING}',
        'no_proxy': 'localhost,127.0.0.1'
    }
}


class Scraping(webdriver.Chrome):
    ERROR = False
    STATUS = None

    def __init__(self, **kwargs):
        """ Initialization """
        options = Options()
        # if config.PROXY_HOST_SCRAPING and config.PROXY_PORT_SCRAPING:
        #     options.add_argument(f'proxy-server={config.PROXY_HOST_SCRAPING}:{config.PROXY_PORT_SCRAPING}')
        if kwargs.get('headless', True):
            options.add_argument('headless')
        options.add_argument("no-sandbox")  # bypass OS security model
        options.add_argument("disable-dev-shm-usage")  # overcome limited resource problems
        super().__init__(ChromeDriverManager().install(), options=options, seleniumwire_options=options_seleniumWire)
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
                # vin = self.find_element_by_name('form:input_vin')
                # submit = self.find_element_by_id('form:suite')
                vin = self.find_element(By.NAME, 'form:input_vin')
                submit = self.find_element(By.ID, 'form:suite')
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
            # username = self.find_element_by_name('form:identifiant2')
            # password = self.find_element_by_name('form:password2')
            # login = self.find_element_by_id('form:login2')
            username = self.find_element(By.NAME, 'form:identifiant2')
            password = self.find_element(By.NAME, 'form:password2')
            login = self.find_element(By.ID, 'form:login2')
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
                # immat = self.find_element_by_name('form:input_immat')
                # submit = self.find_element_by_id('form:suite')
                immat = self.find_element(By.NAME, 'form:input_immat')
                submit = self.find_element(By.ID, 'form:suite')
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
    BRANDS = {
        "Abarth": 2, "Alfa Romeo": 3, "Audi": 4, "Bentley": 5, "BMW": 6, "BMW Classic": 7, "BMW Motorrad": 8,
        "BMW Motorrad Classic": 9, "Citroën": 10, "Citroën DS": 11, "Dacia": 12, "Fiat": 13, "Fiat Professional": 14,
        "Ford": 15, "Ford Commercial": 16, "Hyundai": 17, "Infiniti": 18, "Iveco": 19, "Jaguar": 20, "Jeep": 21,
        "Kia": 22, "Lancia": 23, "Land Rover": 24, "MAN": 25, "Mercedes-Benz": 26, "Mercedes-Benz Trucks": 27,
        "Mercedes-Benz Unimog": 28, "Mercedes-Benz Vans": 29, "MINI": 30, "Mitsubishi": 31, "Nissan": 32, "Opel": 33,
        "Peugeot": 34, "Polestar": 35, "Porsche": 36, "Porsche Classic": 37, "Renault": 38, "SEAT": 39, "Škoda": 40,
        "smart": 41, "Vauxhall": 42, "Volkswagen": 43, "Volkswagen Commercial Vehicles": 44, "Volvo": 45
    }

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
                self.STATUS = "LOGIN"
            except Exception as err:
                self._logger_error('__init__()', err)
                self.quit(error=True)
        else:
            self.ERROR = True

    def brand_select(self, brand="Abarth"):
        try:
            if not self.ERROR and self.STATUS == "HOME":
                if isinstance(brand, str) and self.BRANDS.get(brand):
                    css_select = f"#brands-container-inner > div:nth-child({self.BRANDS[brand]}) > a"
                else:
                    css_select = f"#brands-container-inner > div:nth-child({brand}) > a"
                WebDriverWait(self, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_select))).click()
                self.STATUS = self.get_key_from_brands(brand)
                return True
        except Exception as err:
            self._logger_error('brand_select()', err)
        return False

    def get_home(self):
        result = self.is_element_clicked(By.ID, 'portal')
        if result:
            self.STATUS = "HOME"
        return result

    def search(self, vin_value=None):
        data = {}
        try:
            if not self.ERROR and self.is_element_exist(By.NAME, 'vin'):
                WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, "vin"))).clear()
                # vin = self.find_element_by_name("vin")
                # submit = self.find_element_by_id('vinGo')
                vin = self.find_element(By.NAME, "vin")
                submit = self.find_element(By.ID, 'vinGo')
                if vin_value:
                    vin.send_keys(vin_value)
                submit.click()
                if not self.is_element_clicked(By.XPATH, '/html/body/div[5]/div[3]/div/button'):
                    data = self.result()
        except Exception as err:
            self._logger_error('search()', err)
        return data

    def result(self):
        """
        Corvet data recovery
        :param vin_value: VIN number for the Corvet data
        :return: Corvet data
        //*[@id="vinTabsGeneral"]/table/tbody/tr
        """
        data = {}
        try:
            if not self.ERROR and self.is_element_exist(By.XPATH, '//*/table[@class="vinInfoTable"]/tbody/tr'):
                # for tr in self.find_elements_by_xpath('//*/table[@class="vinInfoTable"]/tbody/tr'):
                for tr in self.find_elements(By.XPATH, '//*/table[@class="vinInfoTable"]/tbody/tr'):
                    # tds = tr.find_elements_by_tag_name('td')
                    tds = tr.find_elements(By.TAG_NAME, 'td')
                    if len(tds) == 1:
                        try:
                            # th = tr.find_element_by_tag_name('th')
                            th = tr.find_element(By.TAG_NAME, 'th')
                            data[th.get_attribute("textContent")] = tds[0].text
                        except NoSuchElementException:
                            pass
                    elif len(tds) >= 2 and tds[0].text != "":
                        data[tds[0].text] = " ".join([td.text for td in tds[1:]])
        except Exception as err:
            self._logger_error('result()', err)
        return data

    def privaty_settings(self):
        WebDriverWait(self, 10).until(EC.presence_of_element_located((By.ID, 'usercentrics-root')))
        # shadow_host = self.find_element_by_id('usercentrics-root')
        shadow_host = self.find_element(By.ID, 'usercentrics-root')
        script = 'return arguments[0].shadowRoot'
        shadow_root_dict = self.execute_script(script, shadow_host)
        id = shadow_root_dict['shadow-6066-11e4-a52e-4f735466cecf']
        shadow_root = WebElement(self, id, w3c=True)
        WebDriverWait(shadow_root, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="uc-accept-all-button"]')))
        # shadow_root.find_element_by_css_selector('[data-testid="uc-accept-all-button"]').click()
        shadow_root.find_element(By.CSS_SELECTOR, '[data-testid="uc-accept-all-button"]').click()

    def login(self):
        """
        Login on the website
        """
        try:
            if not self.ERROR and self.is_element_exist(By.NAME, 'accountLogin'):
                WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'accountLogin')))
                # account = self.find_element_by_name('accountLogin')
                # user = self.find_element_by_name('userLogin')
                # password = self.find_element_by_name('loginBean.password')
                account = self.find_element(By.NAME, 'accountLogin')
                user = self.find_element(By.NAME, 'userLogin')
                password = self.find_element(By.NAME, 'loginBean.password')
                for element, value in {account: self.account, user: self.user, password: self.password}.items():
                    element.clear()
                    element.send_keys(value)
                WebDriverWait(self, 10).until(EC.element_to_be_clickable((By.ID, 'login-btn'))).click()
                self.is_element_clicked(By.ID, 'squeezeout-login-btn')
                if not self.is_element_exist(By.ID, 'logoutLink'):
                    return False
                self.STATUS = "HOME"
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
        result = False
        if not self.ERROR:
            if self.is_element_exist(By.ID, 'logoutLink'):
                result = self.is_element_clicked(By.ID, 'logoutLink')
            else:
                result = self.is_element_clicked(By.ID, 'logout')
            if result is True:
                self.STATUS = "LOGIN"
        return result

    def get_key_from_brands(self, val):
        keys = [key for key, value in self.BRANDS.items() if value == val]
        if keys:
            return keys[0]
        return val


def xml_parser(value):
    data = {"vin": ""}
    try:
        root = ET.XML(value)
        for data_list in root[1]:
            if data_list.tag == "DONNEES_VEHICULE":
                for child in data_list:
                    if child.tag in ["WMI", "VDS", "VIS"]:
                        data['vin'] += child.text
                    elif child.tag in ["DATE_DEBUT_GARANTIE", "DATE_ENTREE_MONTAGE"]:
                        key, value = "DONNEE_{}".format(child.tag), child.text
                        if value:
                            data[key.lower()] = make_aware(datetime.strptime(value, "%d/%m/%Y %H:%M:%S"))
                    else:
                        key, value = "DONNEE_{}".format(child.tag), child.text
                        data[key.lower()] = value
            elif data_list.tag in ["LISTE_ATTRIBUTS", "LISTE_ELECTRONIQUES"]:
                for child in data_list:
                    key, value = "{}_{}".format(child.tag, child.text[:3]), child.text[3:]
                    data[key.lower()] = value
            elif data_list.tag in ["LISTE_ATTRIBUTES_7"]:
                for child in data_list:
                    key, value = "{}_{}".format(child.tag, child.text[:3]), child.text[3:]
                    if value[-2:] == "CD" or value[-2:] == "CP":
                        data[key.lower()] = value[:-2]
                    else:
                        data[key.lower()] = value
            elif data_list.tag == "LISTE_ORGANES":
                for child in data_list:
                    key, value = "{}s_{}".format(child.tag, child.text[:2]), child.text[2:]
                    data[key.lower()] = value
    except (ET.ParseError, KeyError, TypeError):
        data = value
    return data


def xml_sivin_parser(value):
    fields = {
        'carrosserie': 'carrosserie', 'carrosserieCG': 'carrosserie_cg', 'co2': 'co2', 'codeMoteur': 'code_moteur',
        'codifVin': 'codif_vin', 'consExurb': 'cons_exurb', 'consMixte': 'cons_mixte', 'consUrb': 'cons_urb',
        'couleurVehic': 'couleur_vehic', 'cylindree': 'cylindree', 'date1erCir': 'date_1er_cir', 'dateDCG': 'date_dcg',
        'depollution': 'depollution', 'empat': 'empat', 'energie': 'energie', 'genreV': 'genre_v',
        'genreVCG': 'genre_vcg', 'hauteur': 'hauteur', 'immatSiv': 'immat_siv', 'largeur': 'largeur',
        'longueur': 'longueur', 'marque': 'marque', 'marqueCarros': 'marque_carros', 'modeInject': 'mode_inject',
        'modele': 'modele', 'modeleEtude': 'modele_etude', 'modelePrf': 'modele_prf', 'nSerie': 'n_serie',
        'nSiren': 'n_siren', 'nbCylind': 'nb_cylind', 'nbPlAss': 'nb_pl_ass', 'nbPortes': 'nb_portes',
        'nbSoupape': 'nb_soupape', 'nbVitesse': 'nb_vitesse', 'nbVolume': 'nb_volume', 'poidsVide': 'poids_vide',
        'prixVehic': 'prix_vehic', 'propulsion': 'propulsion', 'ptr': 'ptr', 'ptrPrf': 'ptr_prf', 'puisCh': 'puis_ch',
        'puisFisc': 'puis_fisc', 'puisKw': 'puis_kw', 'tpBoiteVit': 'tp_boite_vit', 'turboCompr': 'turbo_compr',
        'type': 'type', 'typeVarVersPrf': 'type_var_vers_prf', 'typeVinCG': 'type_vin_cg', 'version': 'version',
        'pneus': 'pneus', 'latitude': 'latitude'
    }
    data = {}
    try:
        root = ET.fromstring(value)
        for element in root[0][0][0]:
            if element.tag and element.text:
                try:
                    data[fields[element.tag.split('}')[-1]]] = element.text.strip()
                except KeyError as err:
                    exception_type = type(err).__name__
                    logger.error(f"{exception_type} xml_sivin_parser(): {err}")
    except (ET.ParseError, TypeError):
        data = value
    return data
