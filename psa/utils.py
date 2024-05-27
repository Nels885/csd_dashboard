import re
from django.db.models import Q

from utils.regex import REF_PSA_REGEX
from .models import Corvet, Ecu, Multimedia
from squalaetp.models import ProductCode


COLLAPSE_LIST = [
    "media", "prog", "cmb", "emf", "cmm", "bsi", "hdc", "cvm", "vmf", "bpga"
    "display", "audio", "ecu", "cockpit", "security"
]


def collapse_select(xelon_name):
    """
    Modification of the status of the various collapses of the Xelon and Corvet detail pages
    @param xelon_name: Model name found in the Xelon table
    @return: Dictionary of the different names of collapses with their status
    """
    ecu = Ecu.objects.filter(xelon_name=xelon_name)
    media = Multimedia.objects.filter(xelon_name=xelon_name)
    collapse = {key: False for key in COLLAPSE_LIST}
    if ecu:
        ecu_type = ecu.first().type
        # Display collapse
        if ecu_type == "CMB":
            collapse.update({"cmb": True, "display": True})
        elif ecu_type == "EMF":
            collapse.update({"emf": True, "media": True, "display": True, "audio": True})
        # Motor collapse
        elif ecu_type == "CMM":
            collapse.update({"cmm": True, "ecu": True})
        elif ecu_type == "BPGA":
            collapse.update({"bpga": True, "ecu": True})
        # Cockpit collapse
        elif ecu_type == "BSI":
            collapse.update({"bsi": True, "cockpit": True})
        elif ecu_type == "HDC":
            collapse.update({"hdc": True, "cockpit": True})
        elif ecu_type == "VMF":
            collapse.update({'vmf': True, "cockpit": True})
        # Security collapse
        elif ecu_type == "CVM2":
            collapse.update({"cvm": True, "security": True})
    elif media:
        collapse.update({"media": True, "emf": True, "audio": True})
    else:
        collapse.update({key: True for key in ["display", "audio", "ecu", "cockpit", "security"]})
    return collapse


CORVET_LIST = [
    {'hw': 'electronique_14a', 'sw': ['electronique_94a', 'electronique_34a']},
    {'hw': 'electronique_14b', 'sw': ['electronique_94b']},
    {'hw': 'electronique_16b', 'sw': ['electronique_96b']}, {'hw': 'electronique_14d', 'sw': ['electronique_94d']},
    {'hw': 'electronique_12e', 'sw': ['electronique_92e']}, {'hw': 'electronique_14f', 'sw': ['electronique_94f']},
    {'hw': 'electronique_16g', 'sw': ['electronique_96g']}, {'hw': 'electronique_14j', 'sw': ['electronique_94j']},
    {'hw': 'electronique_14k', 'sw': ['electronique_94k']}, {'hw': 'electronique_14l', 'sw': ['electronique_94l']},
    {'hw': 'electronique_16l', 'sw': ['electronique_96l']}, {'hw': 'electronique_14m', 'sw': ['electronique_94m']},
    {'hw': 'electronique_14p', 'sw': ['electronique_94p', 'electronique_34p']},
    {'hw': 'electronique_11q', 'sw': ['electronique_91q']}, {'hw': 'electronique_16q', 'sw': ['electronique_96q']},
    {'hw': 'electronique_14r', 'sw': ['electronique_94r', 'electronique_34r']},
    {'hw': 'electronique_14x', 'sw': ['electronique_94x']}, {'hw': 'electronique_12y', 'sw': ['electronique_92y']}
]


def prod_search(value):
    if value and re.match(REF_PSA_REGEX, value):
        for fields in CORVET_LIST:
            queryset = Corvet.objects.order_by(fields['hw']).filter(**{fields['sw'][0]: value})
            if queryset:
                value = list(queryset.values_list(fields['hw'], flat=True).distinct())[0]
                break
        parts = ProductCode.objects.filter(name__icontains=value)
        if not value[-2:].isdigit():
            value = value[:-2] + '77'
        media = Multimedia.objects.filter(Q(comp_ref__exact=value) | Q(label_ref__exact=value)).first()
        prod = Ecu.objects.filter(Q(comp_ref__exact=value) | Q(label_ref__exact=value)).first()
        vehicles = Corvet.get_vehicles(value)
        return parts, media, prod, vehicles
    return tuple(None for _ in range(4))
