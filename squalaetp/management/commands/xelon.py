from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db.utils import IntegrityError, DataError
from django.db import connection
from django.conf import settings

from squalaetp.models import Xelon

from ._excel_format import ExcelSqualaetp, ExcelsDelayAnalysis

import logging as log


class Command(BaseCommand):
    help = 'Interact with the Xelon table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            help='Update Xelon table',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in Xelon table',
        )

    def handle(self, *args, **options):

        if options['update']:
            if options['filename'] is not None:
                squalaetp = ExcelSqualaetp(options['filename'])
            else:
                squalaetp = ExcelSqualaetp(settings.XLS_SQUALAETP_FILE)

            self.stdout.write("Nombre de ligne dans Excel:     {}".format(squalaetp.nrows))
            self.stdout.write("Noms des colonnes:              {}".format(squalaetp.columns))

            self._update(Xelon, squalaetp.xelon_table(),  "numero_de_dossier", )

        elif options['delete']:
            Xelon.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Xelon, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Xelon"]:
                self.stdout.write("Suppression des données de la table {} terminée!".format(table))

    def _update(self, model, excel_method, columns_name):
        nb_prod_before = model.objects.count()
        excels, nb_prod_update = [], 0
        for file in settings.XLS_DELAY_FILES:
            excels.append(ExcelsDelayAnalysis(file))
        for row in excel_method:
            if len(row[columns_name]):
                try:
                    for excel in excels:
                        row_update = excel.xelon_table(row[columns_name])
                        if len(row_update):
                            row.update(row_update)
                            break
                    log.info(row)
                    product = Xelon.objects.filter(numero_de_dossier=row["numero_de_dossier"])
                    if product:
                        del row["numero_de_dossier"]
                        product.update(**row)
                        nb_prod_update += 1
                    else:
                        m = model(**row)
                        m.save()
                except IntegrityError as err:
                    log.warning("IntegrityError:{}".format(err))
                except DataError as err:
                    self.stdout.write("DataError dossier {} : {}".format(row[columns_name], err))
        nb_prod_after = model.objects.count()
        self.stdout.write("Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
        self.stdout.write("Nombre de produits mis à jour:  {}".format(nb_prod_update))
        self.stdout.write("Nombre de produits total :      {}".format(nb_prod_after))
