import re

from django.utils.translation import gettext as _

from squalaetp.models import Xelon
from psa.models import Corvet

#VIN_PSA_REGEX = r'^[VWZ]((0[LV])|(F[37])|(R[137])|X[A-Z])\w*$'
VIN_PSA_REGEX = r'^[VWYZ]((0[LV])|(A[R])|(F[37])|(R[137])|X[A-Z])\w*$'
VIN_OLD_PSA_REGEX = r'^[VZ]((F[37])|(R[137]))\w*$'
# VIN_PSA_REGEX = r'^V((F[37])|(R[137]))\w{14}$'
COMP_REF_REGEX = r'^[19][468]\d{6}[78][70]$'
XELON_REGEX = r'^[9a-zA-Z]\d{9}$'
URL_REGEX = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
URL_DNS = "cuc.fr.corp"


def comp_ref_isvalid(value):
    if re.match(COMP_REF_REGEX, str(value)):
        return True
    return False


def vin_psa_isvalid(value: str) -> bool:
    if isinstance(value, str) and re.match(VIN_PSA_REGEX, value.upper()):
        return True
    return False


def immat_isvalid(value: str) -> bool:
    if isinstance(value, str):
        if not re.match(XELON_REGEX, value) and (6 < len(value) < 11):
            return True
    return False


def url_isvalid(url: str) -> bool:
    """
        Function for URL validation
        :param url:
            URL
        :return:
            True if valid
            False otherwise
        """
    if isinstance(url, str):
        if re.match(URL_REGEX, url) and (6 < len(url) < 16):
            bytes = url.split('.')
            for ip_bytes in bytes:
                if 0 > int(ip_bytes) or int(ip_bytes) > 255:
                    return False
            return True
        elif URL_DNS in url:
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
    if psa_type and not vin_psa_isvalid(value):
        return _('The V.I.N. is invalid, it should be 17 characters and be part of PSA vehicles')
    elif not re.match(r'^[S-Z]\w{16}$', str(value)):
        return _('The V.I.N. is invalid, it should be 17 characters')
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
    elif re.match(r'^\d{13}\w{6}$', str(value)):
        return value[:8], "OPEL"
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
