from django.db.models.functions import Concat, ExtractDay
from django.db.models import Value, F

from utils.file.export_task import ExportExcelTask
from tools.models import Suptech, BgaTime


class ExportToolsIntoExcelTask(ExportExcelTask):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields = []
        self.noValue = ""

    def run(self, *args, **kwargs):
        excel_type = kwargs.pop('excel_type', 'xlsx')
        model = kwargs.get('table', 'suptech')
        filename = f"{model}_{self.date.strftime('%y-%m-%d_%H-%M')}"
        values_list = self.extract_tools(*args, **kwargs)
        destination_path = self.file(filename, excel_type, values_list)
        return {
            "detail": "Successfully export TOOLS",
            "data": {
                "outfile": destination_path
            }
        }

    def extract_tools(self, *args, **kwargs):
        model = kwargs.get("table", "batch")
        queryset = None
        if model == "suptech":
            self.header = [
                'DATE', 'QUI', 'XELON', 'ITEM', 'TIME', 'INFO', 'RMQ', 'ACTION/RETOUR', 'STATUS', 'DATE_LIMIT',
                'ACTION_LE', 'ACTION_PAR', 'DELAIS_EN_JOURS'
            ]
            fullname = Concat('modified_by__first_name', Value(' '), 'modified_by__last_name')
            day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
            queryset = Suptech.objects.annotate(fullname=fullname, day_number=day_number).order_by('date')
            self.fields = (
                'date', 'user', 'xelon', 'item', 'time', 'info', 'rmq', 'action', 'status', 'deadline', 'modified_at',
                'fullname', 'day_number'
            )
        if model == "bga_time":
            self.header = ['MACHINE', 'DATE', 'HEURE DEBUT', 'DUREE']
            queryset = BgaTime.objects.all()
            self.fields = ('name', 'date', 'start_time', 'duration')
        values_list = queryset.values_list(*self.fields).distinct()
        return values_list
