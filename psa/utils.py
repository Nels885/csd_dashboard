from .models import Ecu, Multimedia


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
