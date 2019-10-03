from squalaetp.models import Corvet
from utils.conf import XML_PATH


def xml_export_file(data, vin):
    dossiers = Corvet.objects.get(vin=vin).xelons.all()
    for queryset in dossiers:
        dossier = queryset.numero_de_dossier
        try:
            with open("{}/{}.xml".format(XML_PATH, dossier), "w") as f:
                f.write(str(data))
        except FileNotFoundError as err:
            print("FileNotFoundError: {}".format(err))
