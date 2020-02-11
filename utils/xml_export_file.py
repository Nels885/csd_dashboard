import os

from squalaetp.models import Corvet
from utils.conf import XML_PATH


def xml_export_file(data, vin):
    dossiers = Corvet.objects.get(vin=vin).xelons.all()
    for queryset in dossiers:
        dossier = queryset.numero_de_dossier
        try:
            if os.path.isfile("{}/{}.xml".format(XML_PATH, dossier)):
                with open("{}/{}.xml".format(XML_PATH, dossier), "w") as f:
                    f.write(str(data))
            else:
                print("{} File exists.".format(dossier))
        except FileNotFoundError as err:
            print("FileNotFoundError: {}".format(err))
