from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import connection

from tools.models import Suptech
from utils.conf import CSD_ROOT
from utils.django.models import defaults_dict
from utils.file.export import ExportExcel, os

from ._csv_suptech import CsvSuptech

import logging as log


class Command(BaseCommand):
    help = 'Interact with the Suptech table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import CSV file',
        )
        parser.add_argument(
            '--import_csv',
            action='store_true',
            dest='import_csv',
            help='Import Suptech CSV file',
        )
        parser.add_argument(
            '--export',
            action='store_true',
            dest='export',
            help='Export Suptech XLS file',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in Suptech table',
        )

    def handle(self, *args, **options):
        self.stdout.write("[SUPTECH] Waiting...")

        if options['import_csv']:
            if options['filename'] is not None:
                excel = CsvSuptech(options['filename'])
                self._update_or_create(Suptech, excel.read())
            else:
                self.stdout.write("Fichier CSV manquant")

        if options['delete']:
            Suptech.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Suptech, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Suptech"]:
                self.stdout.write(self.style.WARNING("Suppression des données de la table {} terminée!".format(table)))

        if options['export']:
            filename = "LOG_SUPTECH_TEST"
            path = os.path.join(CSD_ROOT, "LOGS/LOG_SUPTECH")
            header = [
                'DATE', 'QUI', 'XELON', 'ITEM', 'TIME', 'INFO', 'RMQ', 'ACTION/RETOUR'
            ]
            try:
                queryset = Suptech.objects.all()

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
