import logging
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db.utils import IntegrityError, DataError
from django.db import connection

from raspeedi.models import Programing
from psa.models import Multimedia
from utils.conf import XLS_RASPEEDI_FILE
from utils.django.models import defaults_dict

from ._excel_raspeedi import ExcelPrograming

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Programing table in the database'

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
            help='Delete all data in Programing table',
        )

    def handle(self, *args, **options):
        self.stdout.write("[PROGRAMING] Waiting ...")

        if options['delete']:
            Programing.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Programing])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données des tables Raspeedi terminée!"))

        else:
            if options['filename'] is not None:
                excel = ExcelPrograming(options['filename'])
            else:
                excel = ExcelPrograming(XLS_RASPEEDI_FILE)
            self._programing(excel.read())

    def _programing(self, data):
        nb_before = Programing.objects.count()
        nb_update = 0
        for row in data:
            logger.info(row)
            psa_barcode = row.pop("psa_barcode")
            try:
                multimedia = Multimedia.objects.filter(hw_reference=psa_barcode).first()
                values = {'multimedia': multimedia}
                values.update(defaults_dict(Programing, row))
                obj, created = Programing.objects.update_or_create(psa_barcode=psa_barcode, defaults=values)
                if not created:
                    nb_update += 1
            except IntegrityError as err:
                logger.error(f"[PROGRAMING_CMD] IntegrityError: {psa_barcode} - {err}")
            except DataError as err:
                logger.error(f"[PROGRAMING_CMD] DataError: {psa_barcode} - {err}")
        nb_after = Programing.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[PROGRAMING] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    len(data), nb_after - nb_before, nb_update, nb_after
                )
            )
        )
