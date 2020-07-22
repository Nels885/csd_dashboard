import csv
import datetime
from . import os
import shutil

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
    """ class for exporting data in CSV format """

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
        """ Creation http response """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}_{}.csv"'.format(
            self.filename, self.date.strftime("%y-%m-%d_%H-%M")
        )

        self._csv_writer(response)
        return response

    def file(self, path):
        """ Creation file """
        file = os.path.join(path, "{}.csv".format(self.filename))
        self._file_yesterday(path, file)
        with open(file, 'w', newline='') as csv_file:
            self._csv_writer(csv_file)

    def _csv_writer(self, csv_file):
        """ Formatting data in CSV format """
        writer = csv.writer(csv_file, delimiter=';', lineterminator=';\r\n')
        writer.writerow(self.header)

        for i, query in enumerate(self.valueSet):
            query = tuple([_.strftime("%d/%m/%Y %H:%M:%S") if isinstance(_, datetime.date) else _ for _ in query])
            writer.writerow(query)

    def _file_yesterday(self, path, file):
        """ Creation of the backup file d-1 """
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        if os.path.isfile(file):
            file_date = datetime.datetime.fromtimestamp(os.path.getmtime(file)).date()
            if file_date >= yesterday:
                shutil.copyfile(file, os.path.join(path, "{}J-1.csv".format(self.filename)))
