from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db.utils import IntegrityError
from django.db import connection

from raspeedi.models import Raspeedi
from utils.conf import XLS_RASPEEDI_FILE

from ._excel_raspeedi import ExcelRaspeedi

import logging as log


class Command(BaseCommand):
    help = 'Interact with the Raspeedi table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in raspeedi table',
        )

    def handle(self, *args, **options):

        if options['delete']:
            Raspeedi.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Raspeedi, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write("Suppression des données de la table Raspeedi terminée!")

        else:
            if options['filename'] is not None:
                excel = ExcelRaspeedi(options['filename'])
            else:
                excel = ExcelRaspeedi(XLS_RASPEEDI_FILE)
            self.stdout.write("Nombre de ligne dans Excel:    {}".format(excel.nrows))
            # self.stdout.write("Noms des colonnes:             {}".format(excel.columns))

            nb_before = Raspeedi.objects.count()
            nb_update = 0
            for row in excel.read():
                log.info(row)
                try:
                    obj, created = Raspeedi.objects.update_or_create(ref_boitier=row.pop("ref_boitier"), defaults=row)
                    if not created:
                        nb_update += 1
                except IntegrityError as err:
                    self.stderr.write("IntegrityError: {}".format(err))
            nb_after = Raspeedi.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "Raspeedi data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        excel.nrows, nb_after - nb_before, nb_update, nb_after
                    )
                )
            )
