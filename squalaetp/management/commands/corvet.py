import csv

from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import connection

from squalaetp.models import Corvet
from utils.conf import XLS_SQUALAETP_FILE, XLS_ATTRIBUTS_FILE

from ._excel_squalaetp import ExcelSqualaetp

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
                self._import(Corvet, options['filename'])
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
                excel = ExcelSqualaetp(options['filename'])
            else:
                excel = ExcelSqualaetp(XLS_SQUALAETP_FILE)

            self._update_or_create(Corvet, excel)

    def _update_or_create(self, model, excel):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        for row in excel.corvet_table(XLS_ATTRIBUTS_FILE):
            log.info(row)
            vin = row.pop('vin')
            try:
                obj, created = model.objects.update_or_create(
                    vin=vin, defaults=row
                )
                if not created:
                    nb_prod_update += 1
            except IntegrityError as err:
                self.stderr.write(self.style.ERROR("IntegrityError: {} - {}".format(vin, err)))
            except ValidationError as err:
                self.stderr.write(self.style.ERROR("ValidationError: {} - {}".format(vin, err)))
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[CORVET] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )

    def _import(self, model, csv_file):
        nb_prod_before = model.objects.count()
        with open(csv_file) as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == "vin":
                    continue
                m = model(*row)
                m.save()
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[CORVET] data import completed: ADD = {} | TOTAL = {}".format(
                    nb_prod_after - nb_prod_before, nb_prod_after
                )
            )
        )
