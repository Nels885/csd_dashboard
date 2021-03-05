import logging
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db.utils import IntegrityError, DataError
from django.db import connection

from raspeedi.models import Raspeedi
from psa.models import Multimedia
from utils.conf import XLS_RASPEEDI_FILE
from utils.django.models import defaults_dict

from ._excel_raspeedi import ExcelRaspeedi

# Get an instance of a logger
logger = logging.getLogger('command')


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
        self.stdout.write("[RASPEEDI] Waiting...")

        if options['delete']:
            Raspeedi.objects.all().delete()
            Multimedia.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Raspeedi, Multimedia, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table Raspeedi terminée!"))

        else:
            if options['filename'] is not None:
                excel = ExcelRaspeedi(options['filename'])
            else:
                excel = ExcelRaspeedi(XLS_RASPEEDI_FILE)
            nb_before = Raspeedi.objects.count()
            nb_update = 0
            for row in excel.read():
                logger.info(row)
                ref_boitier = row.pop("ref_boitier")
                try:
                    rasp_values = defaults_dict(Raspeedi, row)
                    obj, created = Raspeedi.objects.update_or_create(ref_boitier=ref_boitier, defaults=rasp_values)
                    if not created:
                        nb_update += 1
                    values = {
                        "name": row.get("produit", ""), "level": row.get("facade", ""),
                        "oe_reference": row.get("ref_mm", ""),
                    }
                    values.update(defaults_dict(Multimedia, row))
                    Multimedia.objects.update_or_create(hw_reference=ref_boitier, defaults=values)
                except IntegrityError as err:
                    logger.error(f"[RASPEEDI_CMD] IntegrityError: {ref_boitier} - {err}")
                except DataError as err:
                    logger.error(f"[RASPEEDI_CMD] DataError: {ref_boitier} - {err}")
            nb_after = Raspeedi.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "[RASPEEDI] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        excel.nrows, nb_after - nb_before, nb_update, nb_after
                    )
                )
            )
