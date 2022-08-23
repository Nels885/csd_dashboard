from psa.models import Ecu


def collapse_select(query):
    ecu = Ecu.objects.filter(xelon_name=query.modele_produit)
    if ecu:
        type = ecu.first().type
        if type == "CMM":
            return {"cmm": True, "ecu": True}
        elif type == "BSI":
            return {"bsi": True, "ecu": True}
        elif type == "HDC":
            return {"hdc": True, "ecu": True}
        elif type == "CVM2":
            return {"cvm": True, "ecu": True}
        elif type == "CMB":
            return {"cmb": True, "display": True}
        elif type == "EMF":
            return {"media": True, "emf": True, "display": True, "audio": True}
    else:
        return {"media": True, "audio": True}
