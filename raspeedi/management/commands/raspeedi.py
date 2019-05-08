from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db.utils import IntegrityError, DataError
from django.db import connection
from django.conf import settings

from raspeedi.models import Raspeedi

import logging as log

import xlrd


class Command(BaseCommand):
    help = 'Interact with the Raspeedi table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--insert',
            action='store_true',
            dest='insert',
            help='Insert Raspeedi table',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in raspeedi table',
        )

    def handle(self, *args, **options):

        if options['insert']:
            nb_prod_before = Raspeedi.objects.count()
            data = xlrd.open_workbook(settings.XLS_RASPEEDI_FILE)
            table = data.sheets()[0]
            nb_lines = table.nrows
            print(f"Nombre de ligne dans Excel:     {nb_lines}")
            columns = table.row_values(0)[:-3]

            for line in range(nb_lines):
                if line == 0:
                    continue  # ignore the first row
                row = table.row_values(line)  # get the data in the ith row
                if len(row[0]):
                    # row[0] = int(row[0])
                    for i in range(4, 6):
                        if row[i] == "O":
                            row[i] = True
                        elif row[i] in ["N", "?", ""]:
                            row[i] = False
                    row_dict = dict(zip(columns, row))
                    print(row_dict)
                    try:
                        m = Raspeedi(**row_dict)
                        m.save()
                    except KeyError as err:
                        log.error(f"Manque la valeur : {err}")
                    except IntegrityError as err:
                        log.error(f"IntegrityError:{err}")
                    except DataError as err:
                        log.error(f"DataError: {err}")
                    # except TypeError as err:
                    #     log.error(f"TypeError: {err}")
            nb_prod_after = Raspeedi.objects.count()
            print(f"Nombre de produits ajoutés :    {nb_prod_after - nb_prod_before}")
            print(f"Nombre de produits total :      {nb_prod_after}")

        elif options['delete']:
            Raspeedi.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Raspeedi, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
