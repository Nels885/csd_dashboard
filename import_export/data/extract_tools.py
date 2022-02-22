from django.db.models.functions import Concat, ExtractDay
from django.db.models import Value, F

from tools.models import Suptech, BgaTime

"""
##################################

Export Tools data to excel format

##################################
"""


def extract_tools(model):
    header = queryset = values_list = None
    if model == "suptech":
        header = [
            'DATE', 'QUI', 'XELON', 'ITEM', 'TIME', 'INFO', 'RMQ', 'ACTION/RETOUR', 'STATUS', 'DATE_LIMIT',
            'ACTION_LE', 'ACTION_PAR', 'DELAIS_EN_JOURS'
        ]
        fullname = Concat('modified_by__first_name', Value(' '), 'modified_by__last_name')
        day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
        queryset = Suptech.objects.annotate(fullname=fullname, day_number=day_number).order_by('date')
        values_list = (
            'date', 'user', 'xelon', 'item', 'time', 'info', 'rmq', 'action', 'status', 'deadline', 'modified_at',
            'fullname', 'day_number'
        )
    if model == "bga_time":
        header = ['MACHINE', 'DATE', 'HEURE DEBUT', 'DUREE']
        queryset = BgaTime.objects.all()
        values_list = ('name', 'date', 'start_time', 'duration')
    fields = values_list
    values_list = queryset.values_list(*values_list).distinct()
    return header, fields, values_list
