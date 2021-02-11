def collapse_select(query):
    if "BSI" in query.modele_produit:
        return {"bsi": True, "ecu": True}
    elif "CALC MOT" in query.famille_produit:
        return {"cmm": True, "ecu": True}
    elif query.modele_produit in ["DISPLAY (COLOR)", "VTH/HUD"]:
        return {"media": True, "emf": True, "display": True, "audio": True}
    else:
        return {"media": True, "audio": True}
