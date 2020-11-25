import csv
import xlwt
import datetime
from . import os
import shutil
import logging

from django.shortcuts import HttpResponse

from psa.models import Corvet
from utils.conf import XML_PATH, TAG_PATH, TAG_LOG_PATH

# Get an instance of a logger
logger = logging.getLogger(__name__)

# # create console handler and set level to debug
# ch = logging.StreamHandler()
#
# # create formatter
# formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
#
# # add formatter to ch
# ch.setFormatter(formatter)
#
# # add ch to logger
# logger.addHandler(ch)


def xml_corvet_file(instance, data, vin):
    try:
        xelon_nb = instance.numero_de_dossier
        os.makedirs(XML_PATH, exist_ok=True)
        file = os.path.join(XML_PATH, xelon_nb + ".xml")
        if not os.path.isfile(file):
            with open(file, "w", encoding='utf-8') as f:
                f.write(str(data))
        else:
            logger.warning("{} File exists.".format(xelon_nb))
    except Corvet.DoesNotExist:
        logger.warning("Xelon number not found")


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
                    with open(file, "w", encoding='utf-8') as f:
                        f.write("Configuration produit effectuée par {}\r\n{}".format(user, comments))
                else:
                    logger.warning("%s File exists.", xelon)
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


class ExportExcel:
    """ class for exporting data in CSV format """

    def __init__(self, queryset, filename, header, values_list=None, excel_type="csv"):
        self.date = datetime.datetime.now()
        self.queryset = queryset
        self.filename = filename
        self.header = header
        if values_list:
            self.valueSet = self.queryset.values_list(*values_list).distinct()
        else:
            self.valueSet = self.queryset.values_list().distinct()
        self.excelType = excel_type

    def http_response(self):
        """ Creation http response """
        if self.excelType == "csv":
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{}_{}.csv"'.format(
                self.filename, self.date.strftime("%y-%m-%d_%H-%M")
            )
            self._csv_writer(response)
        else:
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachement; filename="{}_{}.xls'.format(
                self.filename, self.date.strftime("%y-%m-%d_%H-%M")
            )
            self._xls_writer(response)
        return response

    def file(self, path, copy=True):
        """ Creation file """
        file = os.path.join(path, "{}.{}".format(self.filename, self.excelType))
        if copy:
            self._file_yesterday(path, file)
        try:
            with open(file, 'w+', newline='', encoding='utf-8') as f:
                if self.excelType == "csv":
                    self._csv_writer(f)
                else:
                    self._xls_writer(f)
        except OSError:
            logger.warning('{} File is read-only.'.format(file))

    def _csv_writer(self, response):
        """ Formatting data in CSV format """
        writer = csv.writer(response, delimiter=';', lineterminator=';\r\n')
        writer.writerow(self.header)

        for i, query in enumerate(self.valueSet):
            query = tuple([_.strftime("%d/%m/%Y %H:%M:%S") if isinstance(_, datetime.date) else _ for _ in query])
            writer.writerow(query)

    def _xls_writer(self, response):
        """ Formatting data in Excel format """
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('base')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        for col_num in range(len(self.header)):
            ws.write(row_num, col_num, self.header[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        for i, query in enumerate(self.valueSet):
            query = tuple([_.strftime("%d/%m/%Y %H:%M:%S") if isinstance(_, datetime.date) else _ for _ in query])
            row_num += 1
            for col_num in range(len(query)):
                ws.write(row_num, col_num, query[col_num], font_style)

        wb.save(response)
        return response

    def _file_yesterday(self, path, file):
        """ Creation of the backup file d-1 """
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        if os.path.isfile(file):
            file_date = datetime.datetime.fromtimestamp(os.path.getmtime(file)).date()
            if file_date >= yesterday:
                shutil.copyfile(file, os.path.join(path, "{}J-1.csv".format(self.filename)))
