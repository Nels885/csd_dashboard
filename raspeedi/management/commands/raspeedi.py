from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db.utils import IntegrityError, DataError
from django.db import connection
from django.conf import settings

from raspeedi.models import Raspeedi

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
        verbosity = int(options['verbosity'])

        if options['filename'] is not None:
            excel = ExcelRaspeedi(options['filename'])
        else:
            excel = ExcelRaspeedi(settings.XLS_RASPEEDI_FILE)

        if options['insert']:
            nb_prod_before = Raspeedi.objects.count()

            self.stdout.write("Nombre de ligne dans Excel:    {}".format(excel.nrows))
            self.stdout.write("Noms des colonnes:             {}".format(excel.columns))
            for row in excel.read():
                if verbosity > 1:
                    self.stdout.write(str(row))
                if row["ref_boitier"]:
                    try:
                        m = Raspeedi(**row)
                        m.save()
                    except KeyError as err:
                        self.stderr.write("Manque la valeur : {}".format(err))
                    except IntegrityError as err:
                        self.stderr.write("IntegrityError: {}".format(err))
                    except DataError as err:
                        self.stderr.write("DataError: {}".format(err))
                    except TypeError as err:
                        self.stderr.write("TypeError: {}".format(err))
            nb_prod_after = Raspeedi.objects.count()
            self.stdout.write("Nombre de produits ajoutés :   {}".format(nb_prod_after - nb_prod_before))
            self.stdout.write("Nombre de produits total :     {}".format(nb_prod_after))

        elif options['delete']:
            Raspeedi.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Raspeedi, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            self.stdout.write("Suppression des données de la table Raspeedi terminée!")
