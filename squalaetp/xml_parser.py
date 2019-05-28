import xml.etree.ElementTree as ET


def xml_parser(xml_data):
    data = {"vin": ""}
    tree = ET.XML(xml_data)
    root = tree.getchildren()
    for list in root[1]:
        if list.tag == "DONNEES_VEHICULE":
                for child in list:
                    if child.tag in ["WMI", "VDS", "VIS"]:
                        data['vin'] += child.text
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
    return data
