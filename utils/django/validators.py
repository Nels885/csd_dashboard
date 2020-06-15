import re
import xml.etree.ElementTree as ET

from datetime import datetime

from squalaetp.models import Xelon


def validate_vin(value):
    """
    Function for the VIN validation
    :param value:
        VIN value
    :return:
        Error message if not valid
    """
    if not re.match(r'^VF[37]\w{14}$', str(value)):
        return 'The V.I.N. is invalid, it should be 17 characters and be part of PSA vehicles'
    return None


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
            Xelon.objects.get(numero_de_dossier=value)
            return None
        except Xelon.DoesNotExist:
            return 'Xelon number no exist'
    else:
        return 'Xelon number is invalid'


def validate_psa_barcode(value):
    """
    Function for the Xelon validation
    :param value:
        Xelon value
    :return:
        Error message if not valid
    """
    if not re.match(r'^9[68]\d{8}$', str(value)):
        return 'PSA barcode is invalid'
    return None


def xml_parser(value):
    data = {"vin": ""}
    try:
        tree = ET.XML(value)
        root = tree.getchildren()
        for list in root[1]:
            if list.tag == "DONNEES_VEHICULE":
                for child in list:
                    if child.tag in ["WMI", "VDS", "VIS"]:
                        data['vin'] += child.text
                    elif child.tag in ["DATE_DEBUT_GARANTIE", "DATE_ENTREE_MONTAGE"]:
                        key, value = "DONNEE_{}".format(child.tag), child.text
                        if value:
                            data[key.lower()] = datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
                    else:
                        key, value = "DONNEE_{}".format(child.tag), child.text
                        # print("{} : {}".format(key, value))
                        data[key.lower()] = value
            elif list.tag in ["LISTE_ATTRIBUTS", "LISTE_ELECTRONIQUES"]:
                for child in list:
                    key, value = "{}_{}".format(child.tag, child.text[:3]), child.text[3:]
                    # print("{} : {}".format(key, value))
                    data[key.lower()] = value
            elif list.tag == "LISTE_ORGANES":
                for child in list:
                    key, value = "{}s_{}".format(child.tag, child.text[:2]), child.text[2:]
                    # print("{} : {}".format(key, value))
                    data[key.lower()] = value
    except (ET.ParseError, KeyError):
        data = None
    return data
