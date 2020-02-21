import os

from squalaetp.models import Corvet
from utils.conf import XML_PATH, TAG_PATH, TAG_LOG_PATH


def xml_corvet_file(data, vin):
    xelons = Corvet.objects.get(vin=vin).xelons.all()

    for queryset in xelons:
        xelon_nb = queryset.numero_de_dossier
        os.makedirs(XML_PATH, exist_ok=True)
        file = os.path.join(XML_PATH, xelon_nb + ".xml")
        if not os.path.isfile(file):
            with open(file, "w") as f:
                f.write(str(data))
        else:
            print("{} File exists.".format(xelon_nb))


class Calibre:
    """
    Class allowing the processing of calibration files for Xelon unlocking
    """

    def __init__(self, *args):
        self.paths = list(args)

    def file(self, xelon, comments, user):
        """
        Generate xelon unlock file
        :param xelon: Xelon number
        :param comments: User comment
        """
        if xelon != 'A123456789':
            for path in self.paths:
                file = os.path.join(path, xelon + ".txt")
                os.makedirs(path, exist_ok=True)
                if not os.path.isfile(file):
                    with open(file, "w") as f:
                        f.write("Configuration produit effectuée par {}\r\n{}".format(user, comments))
                else:
                    print("{} File exists.".format(xelon))
                    return False
        return True

    def check(self, xelon):
        """
        Check if the file exists
        :param xelon: Xelon number
        """
        file = os.path.join(self.paths[0], xelon + ".txt")
        if os.path.isfile(file):
            return True
        return False


calibre = Calibre(TAG_PATH, TAG_LOG_PATH)
