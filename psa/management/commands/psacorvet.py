from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import connection

from psa.models import Corvet
from utils.conf import XLS_SQUALAETP_FILE, XLS_ATTRIBUTS_FILE
from utils.django.models import defaults_dict

from ._csv_squalaetp_corvet import CsvCorvet
from ._excel_squalaetp import ExcelCorvet

import logging as log


class Command(BaseCommand):
    help = 'Interact with the Corvet table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )
        parser.add_argument(
            '--import_csv',
            action='store_true',
            dest='import_csv',
            help='import Corvet CSV file',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in Corvet table',
        )

    def handle(self, *args, **options):
        self.stdout.write("[CORVET] Waiting...")

        if options['import_csv']:
            if options['filename'] is not None:
                excel = CsvCorvet(options['filename'])
                self._update_or_create(Corvet, excel.read())
            else:
                self.stdout.write("Fichier CSV manquant")

        elif options['delete']:
            Corvet.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Corvet, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Corvet"]:
                self.stdout.write(self.style.WARNING("Suppression des données de la table {} terminée!".format(table)))

        else:
            if options['filename'] is not None:
                excel = ExcelCorvet(options['filename'], XLS_ATTRIBUTS_FILE)
            else:
                excel = ExcelCorvet(XLS_SQUALAETP_FILE, XLS_ATTRIBUTS_FILE)

            self._update_or_create(Corvet, excel.read())

    def _update_or_create(self, model, data):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        for row in data:
            log.info(row)
            vin = row.pop('vin')
            try:
                defaults = defaults_dict(model, row, 'vin')
                obj, created = model.objects.update_or_create(
                    vin=vin, defaults=defaults
                )
                if not created:
                    nb_prod_update += 1
            except KeyError as err:
                self.stderr.write(self.style.ERROR("KeyError: {}".format(err)))
            except IntegrityError as err:
                self.stderr.write(self.style.ERROR("IntegrityError: {} - {}".format(vin, err)))
            except ValidationError as err:
                self.stderr.write(self.style.ERROR("ValidationError: {} - {}".format(vin, err)))
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[CORVET] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    len(data), nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )
