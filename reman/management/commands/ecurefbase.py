from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.db.utils import DataError

from reman.models import EcuRefBase, EcuModel
from utils.conf import XLS_ECU_REF_BASE

from ._excel_reman import ExcelEcuRefBase

import logging as log


class Command(BaseCommand):
    help = 'Interact with the EcuRefBase table in the database'

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
            help='Delete all data in EcuRefBase table',
        )

    def handle(self, *args, **options):
        if options['delete']:
            EcuRefBase.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [EcuRefBase, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table EcuRefBase terminée!"))
        else:
            if options['filename'] is not None:
                extraction = ExcelEcuRefBase(options['filename'])
            else:
                extraction = ExcelEcuRefBase(XLS_ECU_REF_BASE)

            nb_before = EcuRefBase.objects.count()
            nb_update = 0
            for row in extraction.read():
                log.info(row)
                try:
                    ecu_models = EcuModel.objects.filter(hw_reference=row["hw_reference"])
                    obj, created = EcuRefBase.objects.update_or_create(reman_reference=row["reman_reference"])
                    if not created:
                        nb_update += 1
                    for ecu_model in ecu_models:
                        obj.ecu_models.add(ecu_model)
                except DataError as err:
                    print("DataError: {} - {}".format(row['reman_reference'], err))
            nb_after = EcuRefBase.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "EcuRefBase data update completed: CSV_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        extraction.nrows, nb_after - nb_before, nb_update, nb_after
                    )
                )
            )
