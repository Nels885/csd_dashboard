import tempfile
import datetime

from django.utils import timezone
from celery_progress.backend import ProgressRecorder
from openpyxl import Workbook
from openpyxl.styles import Font

from sbadmin.tasks.base import BaseTask
from psa.models import Multimedia
from psa.templatetags.corvet_tags import get_corvet
from utils.file.export import HTMLFilter, re


class ExportCorvetTask(BaseTask):
    name = "ExportCorvetTask"
    COL_CORVET = {
        'corvet__donnee_ligne_de_produit': 'DON_LIN_PROD', 'corvet__donnee_silhouette': 'DON_SIL',
        'corvet__donnee_genre_de_produit': 'DON_GEN_PROD', 'corvet__attribut_dhb': 'ATT_DHB',
        'corvet__attribut_dlx': 'ATT_DLX', 'corvet__attribut_dun': 'ATT_DUN', 'corvet__attribut_dym': 'ATT_DYM',
        'corvet__attribut_dyr': 'ATT_DYR'
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.date = timezone.now()
        self.noValue = "#"
        self.header = self.fields = []

    def copy_and_get_copied_path(self):
        destination_path = "%s" % (tempfile.gettempdir())
        return destination_path

    def create_workbook(self, workbook: Workbook, header, values_list):
        """ Formatting data in Excel 2010 format """
        progress_recorder = ProgressRecorder(self)
        # Get active worksheet/tab
        ws = workbook.active
        ws.title = 'Feuille 1'

        # Sheet header, first row
        row_num = 1
        total_record = len(values_list)

        # Assign the titles for each cell of the header
        for col_num, column_title in enumerate(header, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.font = Font(bold=True)
            cell.value = column_title

        # Iterate though all values
        for query in values_list:
            row_num += 1
            query = self.query_convert(query)
            query = tuple([self._html_to_string(_) if isinstance(_, str) else _ for _ in query])
            query = self._query_format(query)

            # Assign the data  for each cell of the row
            for col_num, cell_value in enumerate(query, 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = cell_value
            progress_recorder.set_progress(row_num + 1, total=total_record, description="Inserting record into row")
        return workbook

    # def _csv_writer(self, response):
    #     """ Formatting data in CSV format """
    #     writer = csv.writer(response, delimiter=';', lineterminator=';\r\n')
    #     writer.writerow(self.header)
    #
    #     for i, query in enumerate(self.valueSet):
    #         query = tuple([self._html_to_string(_, r'[;,]') if isinstance(_, str) else _ for _ in query])
    #         query = self._query_format(query)
    #         writer.writerow(query)

    def _query_format(self, query):
        query = tuple([_.strftime("%d/%m/%Y %H:%M:%S") if isinstance(_, datetime.date) else _ for _ in query])
        query = tuple([self.noValue if not value else value for value in query])
        return query

    @staticmethod
    def _html_to_string(value, re_sub=None):
        f = HTMLFilter()
        f.feed(value)
        if re_sub:
            return re.sub(re_sub, ' ', f.text)
        else:
            return f.text

    def query_convert(self, data_tuple):
        data_list = [value for value in data_tuple]
        data_tuple = self.get_multimedia_display(data_list)
        return self.get_corvet_display(data_list)

    def get_multimedia_display(self, data_list):
        if 'corvet__btel__name' in self.fields:
            position = self.fields.index('corvet__btel__name')
            for prod in Multimedia.PRODUCT_CHOICES:
                if prod[0] == data_list[position]:
                    data_list[position] = prod[1]
                    break
        return data_list

    def get_corvet_display(self, data_list):
        for field, arg in self.COL_CORVET.items():
            if field in self.fields:
                position = self.fields.index(field)
                if data_list[position]:
                    if arg == 'DON_LIN_PROD':
                        if 'vin' in self.fields and 'VF3' in data_list[self.fields.index('vin')]:
                            arg = 'DON_LIN_PROD 0'
                        elif 'vin' in self.fields and 'VF3' in data_list[self.fields.index('vin')]:
                            arg = 'DON_LIN_PROD 1'
                    data_list[position] = f"{data_list[position]} - {get_corvet(data_list[position], arg)}"
        return data_list