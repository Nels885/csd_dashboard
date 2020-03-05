from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from reman.models import SparePart
from utils.conf import CSV_EXTRACTION_FILE

from ._csv_extraction import CsvSparePart

import logging as log


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
        if options['delete']:
            SparePart.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [SparePart, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write("Suppression des données de la table SparePart terminée!")
        else:
            if options['filename'] is not None:
                extraction = CsvSparePart(options['filename'])
            else:
                extraction = CsvSparePart(CSV_EXTRACTION_FILE)
            self.stdout.write("Nombre de ligne dans Csv:    {}".format(extraction.nrows))
            self.stdout.write("Noms des colonnes:           {}".format(extraction.columns))

            nb_part_before = SparePart.objects.count()
            nb_part_update = 0
            for row in extraction.read():
                log.info(row)
                spare_parts = SparePart.objects.filter(code_produit=row["code_produit"])
                if spare_parts:
                    spare_parts.update(**row)
                    nb_part_update += 1
                else:
                    m = SparePart(**row)
                    m.save()
            nb_part_after = SparePart.objects.count()
            self.stdout.write("Nombre de pièces ajoutés :     {}".format(nb_part_after - nb_part_before))
            self.stdout.write("Nombre de pièces mise à jour:  {}".format(nb_part_update))
            self.stdout.write("Nombre de pièces total :       {}".format(nb_part_after))
