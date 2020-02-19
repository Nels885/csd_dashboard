import os

from squalaetp.models import Corvet
from utils.conf import XML_PATH, TAG_PATH, TAG_LOG_PATH


def xml_corvet_file(data, vin):
    dossiers = Corvet.objects.get(vin=vin).xelons.all()

    for queryset in dossiers:
        dossier = queryset.numero_de_dossier
        os.makedirs(XML_PATH, exist_ok=True)
        file = "{}/{}.xml".format(XML_PATH, dossier)
        if not os.path.isfile(file):
            with open(file, "w") as f:
                f.write(str(data))
        else:
            print("{} File exists.".format(dossier))


def calibre_file(comments, xelon, user):
    paths = [TAG_PATH, TAG_LOG_PATH]
    for path in paths:
        file = "{}/{}.txt".format(path, xelon)
        os.makedirs(path, exist_ok=True)
        if not os.path.isfile(file):
            with open(file, "w") as f:
                f.write("Configuration produit effectuée par {}\r\n{}".format(user, comments))
        else:
            print("{} File exists.".format(xelon))
            return False
    return True
