import os
import re
from glob import glob
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.timezone import make_aware
from django.core.management.base import BaseCommand
from django.db.utils import DataError

from utils.conf import CSD_ROOT
from utils.django.models import defaults_dict

from prog.models import AETLog, AETMeasure


class Command(BaseCommand):
    help = 'Scrap the AET log files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            help='All data',
        )

    def handle(self, *args, **options):
        self.stdout.write("[DAEMON_AET] Waiting...")
        last_24_hours = ""
        if not options['all']:
            last_24_hours = (timezone.datetime.today() - relativedelta(hours=24)).strftime('_%Y-%m-%d_')

        prod_ref = ["DCM3.5", "DCM6.2A", "DCM6.2C", "E98", "EDC15C2", "EDC16C34", "EDC17C60", "EDC17C84", "ME17.9.52", "VD46.1"]
        new_files = []
        for ref in prod_ref:
            path = os.path.join(CSD_ROOT, f'LOGS/LOG_AET/{ref}/*/*{last_24_hours}*.csv')
            for file in glob(path, recursive=True):
                new_files.append((file, ref))

        all_products_list_dictt = []
        for new_file, ref in new_files:
            with open(new_file, "r") as file:
                rows = file.read().splitlines()
                data2 = []
                if not re.search(r'[a-zA-Z]123456789', new_file):
                    for row in rows:
                        data2.append(row.split(";"))
                    if self.aet_check(data2):
                        list_dictt = self.data2dict(data2, new_file, ref)
                        all_products_list_dictt.append(list_dictt)
        self._import_data(all_products_list_dictt)

    @staticmethod
    def get_value(name, value):
        try:
            if isinstance(name, str):
                values = ['XELON', 'MANU_REF', 'COMP_REF']
                data = name.split("_")
                index = values.index(value)
                if len(data) >= index:
                    return data[index]
        except ValueError:
            pass
        return ''

    @staticmethod
    def get_xelon(name):
        return name.split("_")[0]

    @staticmethod
    def get_mat_ref(name):
        return name.split("_")[1]

    @staticmethod
    def get_comp_ref(name):
        return name.split("_")[2]

    @staticmethod
    def aet_check(data):
        try:
            # exclure AET garçonnière
            if data[0][2] == "38-00":
                return False
            # exclure mauvais logs
            if data[-1:][0][2] != "OK":
                return False
        except Exception:
            return False
        return True

    def data2dict(self, data, filename, ref):
        name = os.path.basename(filename)
        mtime = os.stat(filename).st_mtime
        dictt = {}
        list_dictt = []
        for line in data:
            try:
                if '' not in line:
                    dictt["prod_name"] = ref
                    dictt["aet_name"] = ""
                    if "38-" in data[0][2]:
                        dictt["aet_name"] = data[0][2]
                    dictt["xelon"] = self.get_value(name, "XELON")
                    dictt["manu_ref"] = self.get_value(name, 'MANU_REF')
                    dictt["comp_ref"] = self.get_value(name, 'COMP_REF')
                    dictt["date"] = make_aware(datetime.fromtimestamp(mtime))
                    dictt["measure_name"] = line[1]
                    dictt["measured_value"] = line[2].replace(",", ".")
                    dictt["min_value"] = line[4].replace(",", ".")
                    dictt["max_value"] = line[5].replace(",", ".")
                    list_dictt.append(dictt.copy())
            except Exception:
                pass
        return list_dictt

    def _import_data(self, data):
        nb_before = AETLog.objects.count()
        nb_update = 0
        for file in data:
            for row in file:
                log_keys = ['xelon', 'comp_ref', 'manu_ref', 'prod_name', 'aet_name', 'date']
                log_values = defaults_dict(AETLog, {key: row.pop(key, '') for key in log_keys})
                measure_values = defaults_dict(AETMeasure, row)
                try:
                    obj, created = AETLog.objects.get_or_create(**log_values)
                    if not created:
                        nb_update += 1
                    obj.measures.get_or_create(**measure_values)
                except DataError as err:
                    self.stdout.write(
                        self.style.SUCCESS(f"[DAEMON_AET_CMD] DataError: {row} - {err}'")
                    )
        nb_after = AETLog.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"[DAEMON_AET_CMD] data update completed: ADD = {nb_after - nb_before} | UPDATE = {nb_update} | " +
                f"TOTAL = {nb_after}"
            )
        )
