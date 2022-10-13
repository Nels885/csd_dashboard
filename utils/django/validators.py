import re
import xml.etree.ElementTree as ET

from django.utils.translation import gettext as _
from django.utils.timezone import make_aware

from datetime import datetime

from squalaetp.models import Xelon
from psa.models import Corvet

VIN_PSA_REGEX = r'^[VWZ]((0[LV])|(F[37])|(R[137]))\w*$'
VIN_OLD_PSA_REGEX = r'^[VZ]((F[37])|(R[137]))\w*$'
# VIN_PSA_REGEX = r'^V((F[37])|(R[137]))\w{14}$'
COMP_REF_REGEX = r'^[19][468]\d{6}[78][70]$'


def comp_ref_isvalid(value):
    if re.match(COMP_REF_REGEX, str(value)):
        return True
    return False


def vin_psa_isvalid(value):
    if re.match(VIN_PSA_REGEX, str(value)):
        return True
    return False


def validate_vin(value, psa_type=True):
    """
    Function for the VIN validation
    :param value:
        VIN value
    :param psa_type:
        boolean if VIN is PSA vehicle
    :return:
        Error message if not valid
    """
    message = 'The V.I.N. is invalid, it should be 17 characters and be part of PSA vehicles'
    if psa_type and not vin_psa_isvalid(value):
        return _(message)
    elif not re.match(r'^[S-Z]\w{16}$', str(value)):
        return _(message[:-27])
    return None


def validate_nac(value):
    """
    Function VIN or UIN validation for NAC product
    :param value:
        VIN or UIN value
    :return:
        UIN and Error message if not valid
    """
    if vin_psa_isvalid(value):
        try:
            uin = Corvet.objects.get(vin=value).electronique_44x
            if not uin:
                return value, "Numéro de série non trouvé (UIN)"
            value = uin
        except Corvet.DoesNotExist:
            return value, "Ce VIN ne se trouve pas dans la base de données CSD",
    elif not re.match(r'^0D\w{18}$', str(value)):
        return value, _('The V.I.N. or UIN is invalid, it should be 17 or 18 characters and be part of PSA vehicles')
    return value, None


def validate_xelon(value):
    """
    Function for the Xelon validation
    :param value:
        Xelon value
    :return:
        Error message if not valid
    """
    if re.match(r'^[a-zA-Z]\d{9}$', str(value)):
        try:
            if not re.match(r'^[pP]\d{9}$', str(value)):
                Xelon.objects.get(numero_de_dossier=value)
            return None
        except Xelon.DoesNotExist:
            return 'Xelon number no exist'
    else:
        return 'Xelon number is invalid'


def validate_barcode(value):
    """
    Function for the REMAN barcode validation
    :param value:
        barcode value
    :return:
        new value and product customer
    """
    if re.match(r'^9[68]\d{8}\w*$', str(value)):
        return value[:10], "PSA"
    elif re.match(r'^89661-\w{5}$', str(value)):
        return value, "PSA"
    elif re.match(r'55\d{6}$', str(value)):
        return value, "PSA"
    elif re.match(r'^\[\)>\w{55}$', str(value)):
        return value[21:29], "PSA"
    elif re.match(r'^PF\w{16}$', str(value)):
        return value[:10], "VOLVO"
    elif re.match(r'^\d{9}R$', str(value)):
        return value, "PSA"
    return value, None


def validate_identify_number(queryset, value):
    """
    Function for the REMAN Repair validation
    :param queryset:
        queryset of Batch
    :param value:
         identify_number
    :return:
        queryset and Error message if not valid
    """
    message = None
    batch_number = value[:-3] + "000"
    queryset = queryset.filter(batch_number__exact=batch_number)
    if not re.match(r'^[A-Z]\d{9}$', str(value)):
        message = _('The number is not correct, it must consist of an uppercase letter and 9 digits')
    elif value[-3:] == "000":
        message = _("This number is not authorized")
    elif not queryset:
        message = _("The batch does not exist")
    elif queryset and queryset.filter(repairs__identify_number=value):
        message = _("This number exists")
    return queryset, message


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
        'pneus': 'pneus'
    }
    data = {}
    try:
        root = ET.fromstring(value)
        for element in root[0][0][0]:
            if element.tag and element.text:
                data[fields[element.tag.split('}')[-1]]] = element.text.strip()
    except (ET.ParseError, KeyError, TypeError):
        data = value
    return data
