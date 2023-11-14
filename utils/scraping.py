import time
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from django.utils.timezone import make_aware

from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from seleniumwire.webdriver import ChromeOptions as Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constance import config


logger = logging.getLogger('command')


class Scraping(webdriver.Chrome):
    ERROR = False
    STATUS = "INIT"

    def __init__(self, **kwargs):
        """ Initialization """
        options_seleniumwire = {}
        if config.PROXY_HOST_SCRAPING and config.PROXY_PORT_SCRAPING:
            options_seleniumwire['proxy'] = {
                'http': f'{config.PROXY_HOST_SCRAPING}:{config.PROXY_PORT_SCRAPING}',
                'https': f'{config.PROXY_HOST_SCRAPING}:{config.PROXY_PORT_SCRAPING}',
            }
        options = Options()
        options.add_argument("no-sandbox")  # bypass OS security model
        options.add_argument("disable-dev-shm-usage")  # overcome limited resource problems
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        if kwargs.get('headless', True):
            options.add_argument('headless')
        super().__init__(service=Service(), options=options, seleniumwire_options=options_seleniumwire)
        self.set_page_load_timeout(30)

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

    def get(self, *args, **kwargs):
        try:
            self.ERROR = False
            super().get(*args, **kwargs)
        except Exception as err:
            self._logger_error('get()', err)
            self.close()

    def close(self, **kwargs):
        try:
            if self.STATUS not in ["QUIT", "CLOSE"]:
                super().close()
                self.STATUS = "CLOSE"
        except Exception as err:
            self._logger_error('close()', err)
        finally:
            self.ERROR = kwargs.get('error', self.ERROR)

    def quit(self):
        try:
            if self.STATUS != "QUIT":
                super().quit()
                self.STATUS = "QUIT"
        except Exception as err:
            self._logger_error('quit()', err)

    def _logger_error(self, message, err):
        exception_type = type(err).__name__
        logger.error(f"{exception_type} - {message}: {err}")
        self.close(error=True)


class ScrapingCorvet(Scraping):
    """ Scraping data Corvet of the repairnav website"""
    START_URLS = 'https://www.repairnav.com/clarionservice_v2/corvet.xhtml'

    def __init__(self, *args, **kwargs):
        """ Initialization """
        super().__init__(**kwargs)
        self.username = kwargs.get('username', config.CORVET_USER)
        self.password = kwargs.get('password', config.CORVET_PWD)
        self.start(**kwargs)

    def start(self, **kwargs):
        if not kwargs.get('test', False) and self.username and self.password:
            self.get(self.START_URLS)
        else:
            self._logger_error('start()', 'Not username and password')

    def result(self, vin_value=None):
        """
        Corvet data recovery
        :param vin_value: VIN number for the Corvet data
        :return: Corvet data
        """
        if not self.ERROR and self.login() and isinstance(vin_value, str):
            try:
                WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'form:input_vin'))).clear()
                vin = self.find_element(By.NAME, 'form:input_vin')
                submit = self.find_element(By.ID, 'form:suite')
                vin.send_keys(vin_value.upper())
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
            username = self.find_element(By.NAME, 'form:identifiant2')
            password = self.find_element(By.NAME, 'form:password2')
            login = self.find_element(By.ID, 'form:login2')
            for element, value in {username: self.username, password: self.password}.items():
                element.clear()
                element.send_keys(value)
            login.click()
        except Exception as err:
            self._logger_error('login()', err)
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
        if not self.ERROR and self.login() and isinstance(immat_value, str):
            try:
                self.get(self.SIVIN_URLS)
                WebDriverWait(self, 10).until(EC.presence_of_element_located((By.NAME, 'form:input_immat'))).clear()
                immat = self.find_element(By.NAME, 'form:input_immat')
                submit = self.find_element(By.ID, 'form:suite')
                immat.send_keys(immat_value.upper())
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
            self.logout()
            self.get(self.START_URLS)
        else:
            data = "Corvet login Error !!!"
        return data


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
