import os

from squalaetp.models import Corvet
from utils.conf import XML_PATH, TAG_PATH, TAG_LOG_PATH


def xml_file(data, vin):
    dossiers = Corvet.objects.get(vin=vin).xelons.all()
    for queryset in dossiers:
        dossier = queryset.numero_de_dossier
        try:
            file = "{}/{}.xml".format(XML_PATH, dossier)
            if not os.path.isfile(file):
                with open(file, "w") as f:
                    f.write(str(data))
            else:
                print("{} File exists.".format(dossier))
        except FileNotFoundError as err:
            print("FileNotFoundError: {}".format(err))


def calibre_file(comments, xelon, user):
    try:
        status = True
        files = ["{}/{}.txt".format(TAG_PATH, xelon), "{}/{}.txt".format(TAG_LOG_PATH, xelon)]
        for file in files:
            if not os.path.isfile(file):
                with open(file, "w") as f:
                    f.write("Configuration produit effectuée par {}\r\n{}".format(user, comments))
            else:
                print("{} File exists.".format(xelon))
                status = False
                break
    except FileNotFoundError as err:
        print("FileNotFoundError: {}".format(err))
        status = False
    return status
