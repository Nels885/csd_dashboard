import os.path
import tempfile
import datetime

from django.db.models.functions import Cast, TruncSecond
from django.db.models import DateTimeField, CharField
from django.utils import timezone
from celery_progress.backend import ProgressRecorder
from sbadmin import celery_app
from openpyxl import Workbook
from openpyxl.styles import Font

from sbadmin.tasks.base import BaseTask
from squalaetp.models import Xelon
from psa.models import Multimedia
from psa.templatetags.corvet_tags import get_corvet
from .utils import BTEL_HEADER, BTEL_FIELDS
from utils.file.export import HTMLFilter, re


""" source: https://github.com/ebysofyan/django-celery-progress-sample """


class ExportCorvetIntoExcelTask(BaseTask):
    name = "ExportCorvetIntoExcelTask"
    COL_CORVET = {
        'corvet__donnee_ligne_de_produit': 'DON_LIN_PROD', 'corvet__donnee_silhouette': 'DON_SIL',
        'corvet__donnee_genre_de_produit': 'DON_GEN_PROD', 'corvet__attribut_dhb': 'ATT_DHB',
        'corvet__attribut_dlx': 'ATT_DLX', 'corvet__attribut_dun': 'ATT_DUN', 'corvet__attribut_dym': 'ATT_DYM',
        'corvet__attribut_dyr': 'ATT_DYR'
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.noValue = "#"
        self.header = BTEL_HEADER
        self.fields = BTEL_FIELDS

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

    def run(self, *args, **kwargs):
        filename = f"smeg_{int(timezone.now().timestamp())}"
        path = self.copy_and_get_copied_path()
        xelons = Xelon.objects.filter(corvet__isnull=False)
        queryset = xelons.filter(modele_produit__startswith="SMEG").annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = BTEL_FIELDS
        values_list = queryset.values_list(*values_list).distinct()
        destination_path = os.path.join(path, filename + ".xlsx")
        workbook = Workbook()
        workbook = self.create_workbook(workbook, self.header, values_list)
        workbook.save(filename=destination_path)
        return {
            "detail": "Successfully export CORVET",
            "data": {
                "outfile": destination_path
            }
        }


@celery_app.task(bind=True, base=ExportCorvetIntoExcelTask)
def export_corvet_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)
