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
from psa.models import Multimedia, Corvet
from psa.templatetags.corvet_tags import get_corvet
from .utils import BTEL_HEADER, BTEL_FIELDS
from utils.file.export import HTMLFilter, re


""" source: https://github.com/ebysofyan/django-celery-progress-sample """


def extract_corvet(product='corvet'):
    values_list = ()
    header = queryset = None
    xelons = Xelon.objects.filter(corvet__isnull=False)
    if product == "ecu":
        header = [
            'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE', '14A_CMM_HARD',
            '34A_CMM_SOFT_LIVRE', '94A_CMM_SOFT', '44A_CMM_FOURN.NO.SERIE', '54A_CMM_FOURN.DATE.FAB',
            '64A_CMM_FOURN.CODE',
            '84A_CMM_DOTE', 'P4A_CMM_EOBD'
        ]
        queryset = xelons.exclude(corvet__electronique_14a__exact='').annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = (
            'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_debut_garantie',
            'corvet__electronique_14a', 'corvet__electronique_34a', 'corvet__electronique_94a',
            'corvet__electronique_44a',
            'corvet__electronique_54a', 'corvet__electronique_64a', 'corvet__electronique_84a',
            'corvet__electronique_p4a'
        )
    elif product == "bsi":
        header = [
            'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'Modele reel', 'HW', 'SW',
            'DATE_DEBUT_GARANTIE', '14B_BSI_HARD', '94B_BSI_SOFT', '44B_BSI_FOURN.NO.SERIE', '54B_BSI_FOURN.DATE.FAB',
            '64B_BSI_FOURN.CODE', '84B_BSI_DOTE'
        ]

        queryset = xelons.exclude(corvet__electronique_14b__exact='').annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = (
            'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'corvet__bsi__name', 'corvet__bsi__hw',
            'corvet__bsi__sw', 'date_debut_garantie', 'corvet__electronique_14b', 'corvet__electronique_94b',
            'corvet__electronique_44b', 'corvet__electronique_54b', 'corvet__electronique_64b',
            'corvet__electronique_84b',
        )
    elif product == "com200x":
        header = [
            'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE', '16P_HDC_HARD',
            '46P_HDC_FOURN.NO.SERIE', '56P_HDC_FOURN.DATE.FAB', '66P_HDC_FOURN.CODE'
        ]

        queryset = xelons.exclude(corvet__electronique_16p__exact='').annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = (
            'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_debut_garantie',
            'corvet__electronique_16p', 'corvet__electronique_46p', 'corvet__electronique_56p',
            'corvet__electronique_66p'
        )
    elif product == "bsm":
        header = [
            'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE', '16B_BSM_HARD',
            '46B_BSM_FOURN.NO.SERIE', '56B_BSM_FOURN.DATE.FAB', '66B_BSM_FOURN.CODE', '86B_BSM_DOTE', '96B_BSM_SOFT'
        ]

        queryset = xelons.exclude(corvet__electronique_16p__exact='').annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = (
            'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_debut_garantie',
            'corvet__electronique_16b', 'corvet__electronique_46b', 'corvet__electronique_56b',
            'corvet__electronique_66b',
            'corvet__electronique_86b', 'corvet__electronique_96b'
        )
    elif product == "nac":
        header = BTEL_HEADER
        queryset = xelons.filter(modele_produit__contains="NAC").annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = BTEL_FIELDS
    elif product == "rtx":
        header = BTEL_HEADER
        queryset = xelons.filter(modele_produit__startswith="RT").annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = BTEL_FIELDS
    elif product == "smeg":
        header = BTEL_HEADER
        queryset = xelons.filter(modele_produit__startswith="SMEG").annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = BTEL_FIELDS
    elif product == "rneg":
        header = BTEL_HEADER
        queryset = xelons.filter(modele_produit__startswith="RNEG").annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = BTEL_FIELDS
    elif product == "ng4":
        header = BTEL_HEADER
        queryset = xelons.filter(modele_produit__startswith="NG4").annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = BTEL_FIELDS
    elif product == 'corvet':
        header = [
            'V.I.N.', 'DATE_DEBUT_GARANTIE', 'DATE_ENTREE_MONTAGE', 'LIGNE_DE_PRODUIT', 'MARQUE_COMMERCIALE',
            'SILHOUETTE', 'GENRE_DE_PRODUIT', 'DDO', 'DGM', 'DHB', 'DHG', 'DJQ', 'DJY', 'DKX', 'DLX', 'DOI', 'DQM',
            'DQS', 'DRC', 'DRT', 'DTI', 'DUN', 'DWL', 'DWT', 'DXJ', 'DYB', 'DYM', 'DYR', 'DZV', 'GG8', '14F', '14J',
            '14K', '14L', '14R', '14X', '19Z', '44F', '44L', '44X', '54F', '54K', '54L', '84F', '84L', '84X', '94F',
            '94L', '94X', 'DAT', 'DCX', '19H', '49H', '64F', '64X', '69H', '89H', '99H', '14A', '34A', '44A', '54A',
            '64A', '84A', '94A', 'P4A', 'MOTEUR', 'TRANSMISSION', '10', '14B', '20', '44B', '54B', '64B', '84B', '94B',
            '16P', '46P', '56P', '66P', '16B', '46B', '56B', '66B', '86B', '96B'
        ]
        queryset = Corvet.objects.all()
    fields = values_list
    values_list = queryset.values_list(*values_list).distinct()
    return header, fields, values_list


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
        self.date = timezone.now()
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

    def run(self, *args, **kwargs):
        path = self.copy_and_get_copied_path()
        excel_type = kwargs.pop('excel_type', 'csv')
        product = kwargs.pop('product', 'corvet')
        filename = f"{product}_{self.date.strftime('%y-%m-%d_%H-%M')}"
        self.header, self.fields, values_list = extract_corvet(product)
        destination_path = os.path.join(path, f"{filename}.{excel_type}")
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
