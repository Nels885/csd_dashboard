import os
import re
from glob import glob
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.timezone import make_aware
from django.core.management.base import BaseCommand
from constance import config


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
            path = os.path.join(config.CSD_DIR, f'LOGS/LOG_AET/{ref}/*/*{last_24_hours}*.csv')
            new_files = new_files + glob(path, recursive=True)

        all_products_list_dictt = []
        for new_file, ref in new_files:
            with open(new_file, "r") as file:
                rows = file.read().splitlines()
                data2 = []
                # print("vin", vin_from_filename(new_file))
                if not re.search(r'[a-zA-Z]123456789', new_file):
                    for row in rows:
                        data2.append(row.split(";"))
                    if self.aet_check(data2):
                        list_dictt = self.data2dict(data2, new_file, ref)
                        all_products_list_dictt.append(list_dictt)
        print(all_products_list_dictt)

    @staticmethod
    def get_value(name, value):
        try:
            if isinstance(name, str):
                values = ['XELON', 'MAT_REF', 'COMP_REF']
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
                    # print(line)
                    dictt["REF"] = ref
                    dictt["AET"] = data[0][2]
                    dictt["XELON"] = self.get_value(name, "XELON")
                    dictt["MAT_REF"] = self.get_value(name, 'MAT_REF')
                    dictt["COMP_REF"] = self.get_value(name, 'COMP_REF')
                    dictt["DATE"] = make_aware(datetime.fromtimestamp(mtime))
                    dictt["MEASURE_NAME"] = line[1]
                    dictt["VALUE"] = line[2].replace(",", ".")
                    dictt["LOWER_BOND"] = line[4].replace(",", ".")
                    dictt["UPPER_BOND"] = line[5].replace(",", ".")
                    # print(dictt)
                    list_dictt.append(dictt.copy())
            except Exception:
                pass
        # print(list_dictt)
        return list_dictt
