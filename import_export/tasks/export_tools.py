import os.path

from openpyxl import Workbook

from django.db.models.functions import Concat, ExtractDay
from django.db.models import Value, F

from utils.file.export_task import ExportExcelTask
from tools.models import Suptech, BgaTime

"""
##################################

Export Tools data to excel format

##################################
"""


class ExportToolsIntoExcelTask(ExportExcelTask):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.noValue = ""

    def run(self, *args, **kwargs):
        path = self.copy_and_get_copied_path()
        excel_type = kwargs.pop('excel_type', 'xlsx')
        model = kwargs.get('table', 'suptech')
        filename = f"{model}_{self.date.strftime('%y-%m-%d_%H-%M')}"
        self.header, self.fields, values_list = self.extract_tools(*args, **kwargs)
        destination_path = os.path.join(path, f"{filename}.{excel_type}")
        workbook = Workbook()
        workbook = self.create_workbook(workbook, self.header, values_list)
        workbook.save(filename=destination_path)
        return {
            "detail": "Successfully export TOOLS",
            "data": {
                "outfile": destination_path
            }
        }

    @staticmethod
    def extract_tools(*args, **kwargs):
        model = kwargs.get("table", "batch")
        header = queryset = fields = None
        if model == "suptech":
            header = [
                'DATE', 'QUI', 'XELON', 'ITEM', 'TIME', 'INFO', 'RMQ', 'ACTION/RETOUR', 'STATUS', 'DATE_LIMIT',
                'ACTION_LE', 'ACTION_PAR', 'DELAIS_EN_JOURS'
            ]
            fullname = Concat('modified_by__first_name', Value(' '), 'modified_by__last_name')
            day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
            queryset = Suptech.objects.annotate(fullname=fullname, day_number=day_number).order_by('date')
            fields = (
                'date', 'user', 'xelon', 'item', 'time', 'info', 'rmq', 'action', 'status', 'deadline', 'modified_at',
                'fullname', 'day_number'
            )
        if model == "bga_time":
            header = ['MACHINE', 'DATE', 'HEURE DEBUT', 'DUREE']
            queryset = BgaTime.objects.all()
            fields = ('name', 'date', 'start_time', 'duration')
        values_list = queryset.values_list(*fields).distinct()
        return header, fields, values_list
