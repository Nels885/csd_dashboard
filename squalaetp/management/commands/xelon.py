from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.core.exceptions import FieldDoesNotExist
from django.db.utils import IntegrityError, DataError
from django.db import connection

from squalaetp.models import Xelon
from utils.conf import XLS_SQUALAETP_FILE, XLS_DELAY_FILES

from ._excel_squalaetp import ExcelSqualaetp
from ._excel_delay_analysis import ExcelDelayAnalysis

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
            '--fix_update',
            action='store_true',
            dest='fix_update',
            help='Fix Update Xelon table',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in Xelon table',
        )

    def handle(self, *args, **options):

        if options['update'] or options['fix_update']:
            if options['filename'] is not None:
                squalaetp = ExcelSqualaetp(options['filename'])
            else:
                squalaetp = ExcelSqualaetp(XLS_SQUALAETP_FILE)

            self.stdout.write("Nombre de ligne dans Excel:     {}".format(squalaetp.nrows))
            # self.stdout.write("Noms des colonnes:              {}".format(list(squalaetp.columns)))

            self._squalaetp_file(Xelon, squalaetp.xelon_table(), "numero_de_dossier")
            if options['update']:
                self._delay_files(Xelon)
            else:
                self._fix_delay_files(Xelon)

        elif options['delete']:
            Xelon.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Xelon, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Xelon"]:
                self.stdout.write("Suppression des données de la table {} terminée!".format(table))

    def _squalaetp_file(self, model, excel_method, columns_name):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        for row in excel_method:
            if len(row[columns_name]):
                try:
                    log.info(row)
                    product = Xelon.objects.filter(numero_de_dossier=row["numero_de_dossier"])
                    if product:
                        product.update_or_create(**row)
                        nb_prod_update += 1
                    else:
                        m = model(**row)
                        m.save()
                except IntegrityError as err:
                    log.warning("IntegrityError:{}".format(err))
                except DataError as err:
                    self.stdout.write("DataError dossier {} : {}".format(row[columns_name], err))
        nb_prod_after = model.objects.count()
        self.stdout.write("[SQUALAETP] Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
        self.stdout.write("[SQUALAETP] Nombre de produits mis à jour:  {}".format(nb_prod_update))
        self.stdout.write("[SQUALAETP] Nombre de produits total :      {}".format(nb_prod_after))

    def _delay_files(self, model):
        excels, nb_prod_update = [], 0
        for file in XLS_DELAY_FILES:
            excels.append(ExcelDelayAnalysis(file))
        nb_prod_before = model.objects.count()
        for excel in excels:
            for row in excel.table():
                try:
                    if len(row):
                        product = Xelon.objects.filter(numero_de_dossier=row["numero_de_dossier"])
                        if product:
                            del row["numero_de_dossier"]
                            product.update(**row)
                            nb_prod_update += 1
                except IntegrityError as err:
                    log.warning("IntegrityError:{}".format(err))
                except DataError as err:
                    self.stdout.write("DataError dossier {} : {}".format(row["numero_de_dossier"], err))
                except FieldDoesNotExist as err:
                    self.stdout.write("FieldDoesNotExist row {} : {}".format(row, err))
        nb_prod_after = model.objects.count()
        self.stdout.write("[DELAY] Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
        self.stdout.write("[DELAY] Nombre de produits mis à jour : {}".format(nb_prod_update))
        self.stdout.write("[DELAY] Nombre de produits total :      {}".format(nb_prod_after))

    def _fix_delay_files(self, model):
        excels, nb_prod_update = [], 0
        for file in XLS_DELAY_FILES:
            excels.append(ExcelDelayAnalysis(file))
        nb_prod_before = model.objects.count()
        model.objects.exclude(
            type_de_cloture__in=['Réparé', 'Rebut'], date_retour__isnull=True).update(type_de_cloture='Réparé')
        for excel in excels:
            for row in excel.table():
                try:
                    if len(row):
                        product = Xelon.objects.filter(numero_de_dossier=row["numero_de_dossier"])
                        if product:
                            del row["numero_de_dossier"]
                            product.update(type_de_cloture='')
                            product.update(**row)
                            nb_prod_update += 1
                except IntegrityError as err:
                    log.warning("IntegrityError:{}".format(err))
                except DataError as err:
                    self.stdout.write("DataError dossier {} : {}".format(row["numero_de_dossier"], err))
                except FieldDoesNotExist as err:
                    self.stdout.write("FieldDoesNotExist row {} : {}".format(row, err))
        nb_prod_after = model.objects.count()
        self.stdout.write("[DELAY] Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
        self.stdout.write("[DELAY] Nombre de produits mis à jour : {}".format(nb_prod_update))
        self.stdout.write("[DELAY] Nombre de produits total :      {}".format(nb_prod_after))
