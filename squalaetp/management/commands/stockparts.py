from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.db.utils import IntegrityError, DataError

from squalaetp.models import ProductCode, Stock
from utils.conf import CSV_EXTRACTION_FILE

from ._csv_extraction import CsvSparePart

import logging as log


class Command(BaseCommand):
    help = 'Interact with the Stock table in the database'

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
        if options['delete']:
            Stock.objects.all().delete()
            ProductCode.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Stock, ProductCode, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write(self.style.WARNING("Suppression des données de la table SparePart terminée!"))
        else:
            if options['filename'] is not None:
                extraction = CsvSparePart(options['filename'])
            else:
                extraction = CsvSparePart(CSV_EXTRACTION_FILE)

            nb_part_before = ProductCode.objects.count()
            nb_part_update = 0
            for row in extraction.read():
                log.info(row)
                code_magasin = row.pop("code_magasin")
                code_produit = row.pop("code_produit")
                code_zone = row.pop("code_zone")
                code_emplacement = row.pop("code_emplacement")
                try:
                    part_obj, part_created = ProductCode.objects.get_or_create(name=code_produit)
                    obj, created = Stock.objects.update_or_create(
                        code_magasin=code_magasin, code_zone=code_zone,
                        code_emplacement=code_emplacement, code_produit=part_obj, defaults=row
                    )
                    if not created:
                        nb_part_update += 1
                except IntegrityError as err:
                    print("IntegrityError: {} - {}".format(code_produit, err))
                except ProductCode.MultipleObjectsReturned as err:
                    print("MultipleObjectsReturned: {} - {}".format(code_produit, err))
                except DataError as err:
                    print("DataError: {} - {}".format(code_produit, err))
            nb_part_after = ProductCode.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "SpareParts data update completed: CSV_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        extraction.nrows, nb_part_after - nb_part_before, nb_part_update, nb_part_after
                    )
                )
            )
