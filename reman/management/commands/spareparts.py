import logging
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.db.utils import IntegrityError

from reman.models import SparePart
from utils.conf import CSV_EXTRACTION_FILE

from ._csv_extraction import CsvSparePart

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Interact with the SparePart table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import CSV file',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in SparePart table',
        )

    def handle(self, *args, **options):
        self.stdout.write("[SPAREPARTS] Waiting...")

        if options['delete']:
            SparePart.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [SparePart, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table SparePart terminée!"))
        else:
            if options['filename'] is not None:
                extraction = CsvSparePart(options['filename'])
            else:
                extraction = CsvSparePart(CSV_EXTRACTION_FILE)

            nb_part_before = SparePart.objects.count()
            nb_part_update = 0
            for row in extraction.read():
                logger.info(row)
                code_produit = row.pop("code_produit")
                try:
                    if "REMAN PSA" in row['code_zone']:
                        obj, created = SparePart.objects.update_or_create(
                            code_produit=code_produit, defaults=row
                        )
                        if not created:
                            nb_part_update += 1
                except IntegrityError as err:
                    logger.error(f"[SPAREPARTS_CMD] IntegrityError: {code_produit} - {err}")
                except SparePart.MultipleObjectsReturned as err:
                    logger.error(f"[SPAREPARTS_CMD] MultipleObjectsReturned: {code_produit} - {err}")
            nb_part_after = SparePart.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "[SPAREPARTS] Data update completed: CSV_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        extraction.nrows, nb_part_after - nb_part_before, nb_part_update, nb_part_after
                    )
                )
            )
