from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models.functions import Concat, ExtractDay
from django.db.models import Value, F

from utils.file.export_task import ExportExcelTask
from tools.models import Suptech, BgaTime, RaspiTime


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
        model = kwargs.get("table", "suptech")
        datedelta = kwargs.get("date_delta")
        queryset = last_months = None
        if datedelta and datedelta.isnumeric():
            last_months = timezone.datetime.today() + relativedelta(months=-int(datedelta))
        if model == "bga_time":
            self.header = ['MACHINE', 'DATE', 'HEURE_DEBUT', 'HEURE_FIN', 'DUREE']
            if last_months:
                queryset = BgaTime.objects.filter(date__gte=last_months)
            else:
                queryset = BgaTime.objects.all()
            self.fields = ('name', 'date', 'start_time', 'end_time', 'duration')
        if model == "raspi_time":
            self.header = ['MACHINE', 'TYPE', 'DATE', 'HEURE_DEBUT', 'HEURE_FIN', 'DUREE', 'N°_XELON']
            if last_months:
                queryset = RaspiTime.objects.filter(date__gte=last_months)
            else:
                queryset = RaspiTime.objects.all()
            self.fields = ('name', 'type', 'date', 'start_time', 'end_time', 'duration', 'xelon')
        values_list = queryset.values_list(*self.fields).distinct()
        return values_list


SUPTECH_DICT = {
    'min': [
        ('N° SUPTECH', 'id'), ('DATE', 'date'), ('QUI', 'user'), ('XELON', 'xelon'), ('PRODUIT', 'product'),
        ('ITEM', 'item'), ('CATEGORY', 'category__name'), ('TRAIT_48H', 'is_48h')
    ],
    'time': [('TIME', 'time')],
    'info': [('INFO', 'info')],
    'rmq': [('RMQ', 'rmq')],
    'action': [('ACTION/RETOUR', 'action')],
    'status': [('STATUS', 'status')],
    'deadline': [('DATE_LIMIT', 'deadline')],
    'modified_at': [('ACTION_LE', 'modified_at')],
    'fullname': [('ACTION_PAR', 'fullname')],
    'day_number': [('DELAIS_EN_JOURS', 'day_number')],
}


class ExportSuptechIntoExcelTask(ExportExcelTask):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields = []
        self.noValue = ""

    def run(self, *args, **kwargs):
        excel_type = kwargs.pop('excel_type', 'xlsx')
        filename = "suptech"
        values_list = self.extract(*args, **kwargs)
        destination_path = self.file(filename, excel_type, values_list)
        return {
            "detail": "Successfully export SUPTECHS",
            "data": {
                "outfile": destination_path
            }
        }

    def extract(self, *args, **kwargs):
        datedelta = kwargs.get("date_delta")
        queryset = Suptech.objects.all()
        if kwargs.get('category', None):
            queryset = queryset.filter(category=kwargs.get('category'))
        queryset = self.is_48h_valid(queryset, **kwargs)
        if kwargs.get('start_date', None):
            queryset = queryset.filter(created_at__gte=kwargs.get('start_date'))
        if kwargs.get('end_date', None):
            queryset = queryset.filter(created_at__lte=kwargs.get('end_date'))
        if datedelta and datedelta.isnumeric():
            last_months = timezone.datetime.today() + relativedelta(months=-int(datedelta))
            queryset = queryset.filter(date__gte=last_months)
        fullname = Concat('modified_by__first_name', Value(' '), 'modified_by__last_name')
        day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
        queryset = queryset.annotate(fullname=fullname, day_number=day_number).order_by('date')
        self._select_columns(**kwargs)
        values_list = queryset.values_list(*self.fields).distinct()
        return values_list

    @staticmethod
    def is_48h_valid(queryset, **kwargs):
        if kwargs.get('is_48h', '').lower() == 'true':
            queryset = queryset.filter(is_48h=True)
        elif kwargs.get('is_48h', '').lower() == 'false':
            queryset = queryset.filter(is_48h=False)
        return queryset

    def _select_columns(self, **kwargs):
        data_list = SUPTECH_DICT['min']
        for col in kwargs.get('columns', []):
            data_list = data_list + SUPTECH_DICT.get(col, [])
        self.header, self.fields = self.get_header_fields(data_list)
