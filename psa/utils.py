from .models import Ecu


COLLAPSE_LIST = [
    "media", "prog", "cmb", "emf", "cmm", "bsi", "hdc", "cvm", 'vmf',
    "display", "audio", "ecu", "cockpit"
]


def collapse_select(xelon_name):
    """
    Modification of the status of the various collapses of the Xelon and Corvet detail pages
    @param xelon_name: Model name found in the Xelon table
    @return: Dictionary of the different names of collapses with their status
    """
    ecu = Ecu.objects.filter(xelon_name=xelon_name)
    collapse = {key: False for key in COLLAPSE_LIST}
    if ecu:
        type = ecu.first().type
        if type == "CMM":
            collapse.update({"cmm": True, "ecu": True})
        elif type == "BSI":
            collapse.update({"bsi": True, "ecu": True})
        elif type == "HDC":
            collapse.update({"hdc": True, "ecu": True})
        elif type == "CVM2":
            collapse.update({"cvm": True, "ecu": True})
        elif type == "VMF":
            collapse.update({'vmf': True, "ecu": True})
        elif type == "CMB":
            collapse.update({"cmb": True, "display": True})
        elif type == "EMF":
            collapse.update({"media": True, "emf": True, "display": True, "audio": True})
    else:
        collapse.update({"media": True, "audio": True, "emf": True})
    return collapse
