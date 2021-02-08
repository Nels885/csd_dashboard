from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import connection

from tools.models import Suptech
from utils.conf import CSD_ROOT
from utils.django.models import defaults_dict
from utils.file.export import ExportExcel, os

from ._file_suptech import CsvSuptech, ExcelSuptech

import logging as log


class Command(BaseCommand):
    help = 'Interact with the Suptech table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in Suptech table',
        )
        parser.add_argument(
            '--first',
            action='store_true',
            dest='first',
            help='Adding first data in Suptech table',
        )

    def handle(self, *args, **options):
        self.stdout.write("[SUPTECH] Waiting...")
        path = os.path.join(CSD_ROOT, "LOGS/LOG_SUPTECH")
        filename = "LOG_SUPTECH"

        if options['delete']:
            Suptech.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Suptech, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Suptech"]:
                self.stdout.write(self.style.WARNING("Suppression des données de la table {} terminée!".format(table)))

        elif options['first']:
            excel = ExcelSuptech(os.path.join(path, filename + ".xls"))
            self._update_or_create(Suptech, excel.read())
            csv = CsvSuptech(os.path.join(path, filename + ".csv"))
            self._update_or_create(Suptech, csv.read())
            self._export(path, filename)
        else:
            if os.path.exists(os.path.join(path, filename + ".csv")):
                csv = CsvSuptech(os.path.join(path, filename + ".csv"))
                self._create(Suptech, csv.read())
                # os.remove(os.path.join(path, filename + ".csv"))
                with open(os.path.join(path, filename + ".csv"), "w"):
                    pass
            else:
                self.stdout.write(self.style.WARNING("The file does not exist"))
            excel = ExcelSuptech(os.path.join(path, filename + ".xls"))
            self._update_or_create(Suptech, excel.read())
            self._export(path, filename)

    def _create(self, model, data):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        for row in data:
            log.info(row)
            try:
                defaults = defaults_dict(model, row)
                model.objects.create(**defaults)
                nb_prod_update += 1
            except KeyError as err:
                self.stderr.write(self.style.ERROR("KeyError: {}".format(err)))
            except IntegrityError as err:
                self.stderr.write(self.style.ERROR("IntegrityError: {} - {}".format(row.get('item'), err)))
            except ValidationError as err:
                self.stderr.write(self.style.ERROR("ValidationError: {} - {}".format(row.get('item'), err)))
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[SUPTECH] data create completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    len(data), nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )

    def _update_or_create(self, model, data):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        for row in data:
            log.info(row)
            date = row.pop('date')
            user = row.pop('user', '')
            xelon = row.pop('xelon', '')
            item = row.pop('item', '')
            time = row.pop('time', '')
            info = row.pop('info', '')
            try:
                defaults = defaults_dict(model, row)
                obj, created = model.objects.update_or_create(
                    date=date, user=user, xelon=xelon, item=item, time=time, info=info, defaults=defaults
                )
                if not created:
                    nb_prod_update += 1
            except KeyError as err:
                self.stderr.write(self.style.ERROR("KeyError: {}".format(err)))
            except IntegrityError as err:
                self.stderr.write(self.style.ERROR("IntegrityError: {} - {}".format(row.get('item'), err)))
            except ValidationError as err:
                self.stderr.write(self.style.ERROR("ValidationError: {} - {}".format(row.get('item'), err)))
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[SUPTECH] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    len(data), nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )

    def _export(self, path, filename):
        header = [
            'DATE', 'QUI', 'XELON', 'ITEM', 'TIME', 'INFO', 'RMQ', 'ACTION/RETOUR'
        ]
        try:
            queryset = Suptech.objects.all().order_by('date')

            values_list = ('date', 'user', 'xelon', 'item', 'time', 'info', 'rmq', 'action')

            error = ExportExcel(queryset=queryset, filename=filename, header=header, values_list=values_list,
                                excel_type='xls', novalue="").file(path, False)
            if error:
                self.stdout.write(
                    self.style.ERROR(
                        "[SUPTECH] Export error because {}.xls file is read-only!".format(
                            os.path.join(path, filename)
                        )
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        "[SUPTECH] Export completed: NB_FILE = {} | FILE = {}.xls".format(
                            queryset.count(), os.path.join(path, filename)
                        )
                    )
                )
        except FileNotFoundError as err:
            self.stdout.write(self.style.ERROR("[SUPTECH] {}".format(err)))
