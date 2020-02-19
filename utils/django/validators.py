import re

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
