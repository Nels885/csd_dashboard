import csv
import datetime
from . import os

from django.shortcuts import HttpResponse

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


class ExportCsv:

    def __init__(self, queryset, filename, header, values_list=None):
        self.date = datetime.datetime.now()
        self.queryset = queryset
        self.filename = filename
        self.header = header
        if values_list:
            self.valueSet = self.queryset.values_list(*values_list).distinct()
        else:
            self.valueSet = self.queryset.values_list().distinct()

    def http_response(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}_{}.csv"'.format(
            self.filename, self.date.strftime("%y-%m-%d_%H-%M")
        )

        writer = csv.writer(response, delimiter=';', lineterminator=';\r\n')
        writer.writerow(self.header)

        for i, query in enumerate(self.valueSet):
            query = tuple([_.strftime("%d/%m/%Y %H:%M:%S") if isinstance(_, datetime.date) else _ for _ in query])
            writer.writerow(query)

        return response

    def file(self, path):
        file = os.path.join(path, "{}.csv".format(self.filename))
        with open(file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', lineterminator=';\r\n')
            writer.writerow(self.header)

            for i, query in enumerate(self.valueSet):
                query = tuple([_.strftime("%d/%m/%Y %H:%M:%S") if isinstance(_, datetime.date) else _ for _ in query])
                writer.writerow(query)
