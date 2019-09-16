import csv

from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db.utils import IntegrityError
from django.db import connection
from django.conf import settings

from squalaetp.models import Corvet, CorvetBackup

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
            '--insert',
            action='store_true',
            dest='insert',
            help='Insert Corvet table',
        )
        parser.add_argument(
            '--import_csv',
            action='store_true',
            dest='import_csv',
            help='import Corvet CSV file',
        )
        parser.add_argument(
            '--backup_insert',
            action='store_true',
            dest='backup_insert',
            help='Insert Corvet Backup table',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in Corvet table',
        )

    def handle(self, *args, **options):

        if options['insert']:
            if options['filename'] is not None:
                excel = ExcelSqualaetp(options['filename'])
            else:
                excel = ExcelSqualaetp(settings.XLS_SQUALAETP_FILE)
            self.stdout.write("Nombre de ligne dans Excel:     {}".format(excel.nrows))
            self.stdout.write("Noms des colonnes:              {}".format(excel.columns))

            self._insert(Corvet, excel.corvet_table(settings.XLS_ATTRIBUTS_FILE), "vin")

        elif options['import_csv']:
            if options['filename'] is not None:
                self._import(Corvet, options['filename'])
            else:
                self.stdout.write("Fichier CSV manquant")

        elif options['backup_insert']:
            if options['filename'] is not None:
                excel = ExcelSqualaetp(options['filename'])
            else:
                excel = ExcelSqualaetp(settings.XLS_SQUALAETP_FILE)
            self.stdout.write("Nombre de ligne dans Excel:     {}".format(excel.nrows))
            self.stdout.write("Noms des colonnes:              {}".format(excel.columns))

            self._insert(CorvetBackup, excel.corvet_backup_table(), "vin")

        elif options['delete']:
            Corvet.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Corvet, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Corvet"]:
                self.stdout.write("Suppression des données de la table {} terminée!".format(table))

    def _insert(self, model, excel_method, columns_name):
        nb_prod_before = model.objects.count()
        for row in excel_method:
            log.info(row)
            if len(row[columns_name]):
                try:
                    m = model(**row)
                    m.save()
                except IntegrityError as err:
                    log.warning("IntegrityError:{}".format(err))
        nb_prod_after = model.objects.count()
        self.stdout.write("Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
        self.stdout.write("Nombre de produits total :      {}".format(nb_prod_after))

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
        self.stdout.write("Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
        self.stdout.write("Nombre de produits total :      {}".format(nb_prod_after))
