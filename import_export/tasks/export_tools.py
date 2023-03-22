from dateutil.relativedelta import relativedelta
from django.utils import timezone
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
        filename = f"{model}"
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
        datedelta = kwargs.get("date_delta")
        queryset = last_months = None
        if datedelta and datedelta.isnumeric():
            last_months = timezone.datetime.today() + relativedelta(months=-int(datedelta))
        if model == "suptech":
            self.header = [
                'N° SUPTECH', 'DATE', 'QUI', 'XELON', 'PRODUIT', 'ITEM', 'TIME', 'INFO', 'RMQ', 'ACTION/RETOUR',
                'STATUS', 'DATE_LIMIT', 'ACTION_LE', 'ACTION_PAR', 'DELAIS_EN_JOURS'
            ]
            if last_months:
                queryset = Suptech.objects.filter(date__gte=last_months)
            else:
                queryset = Suptech.objects.all()
            fullname = Concat('modified_by__first_name', Value(' '), 'modified_by__last_name')
            day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
            queryset = queryset.annotate(fullname=fullname, day_number=day_number).order_by('date')
            self.fields = (
                'id', 'date', 'user', 'xelon', 'product', 'item', 'time', 'info', 'rmq', 'action', 'status', 'deadline',
                'modified_at', 'fullname', 'day_number'
            )
        if model == "bga_time":
            self.header = ['MACHINE', 'DATE', 'HEURE DEBUT', 'DUREE']
            if last_months:
                queryset = BgaTime.objects.filter(date__gte=last_months)
            else:
                queryset = BgaTime.objects.all()
            self.fields = ('name', 'date', 'start_time', 'duration')
        values_list = queryset.values_list(*self.fields).distinct()
        return values_list
