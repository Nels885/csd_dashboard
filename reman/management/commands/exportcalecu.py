from django.core.management.base import BaseCommand

from utils.file import LogFile
from utils.conf import CSD_ROOT


class Command(BaseCommand):
    help = 'Export PSA ECU CAL list for REMAN'

    def handle(self, *args, **options):
        log_file = LogFile(CSD_ROOT)
        file_name = "liste_CAL_PSA.txt"
        nb_cal = log_file.export_cal_xelon(file_name)
        self.stdout.write(
            self.style.SUCCESS("export ECU CAL completed: NB_CAL = {} | FILE = {}".format(nb_cal, file_name))
        )
