from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError, DataError
from django.db import connection
from django.conf import settings

from squalaetp.models import Xelon, CorvetBackup, Corvet

from ._excel_format import ExcelSqualaetp

import logging as log


class Command(BaseCommand):
    help = 'Interact with the Squalaetp tables in the database'

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
            help='update all data in Squalaetp tables',
        )
        parser.add_argument(
            '--relations',
            action='store_true',
            dest='relations',
            help='add the relationship between the xelon and corvet tables',
        )
        parser.add_argument(
            '--backup_insert',
            action='store_true',
            dest='backup_insert',
            help='Insert Corvet Backup table',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete all data in Squalaetp tables',
        )

    def handle(self, *args, **options):

        if options['filename'] is not None:
            excel = ExcelSqualaetp(options['filename'])
        else:
            excel = ExcelSqualaetp(settings.XLS_SQUALAETP_FILE)
        self.stdout.write("Nombre de ligne dans Excel:     {}".format(excel.nrows))
        self.stdout.write("Noms des colonnes:              {}".format(excel.columns))

        if options['update']:
            pass

        elif options['relations']:
            xelon_files = []
            count = 0
            for xelon in Xelon.objects.all():
                try:
                    corvet = Corvet.objects.get(pk=xelon.vin)
                    corvet.xelons.add(xelon)
                    count += 1
                except ObjectDoesNotExist:
                    xelon_files.append(xelon.numero_de_dossier)
            self.stdout.write("pas de relation pour les dossier Xelon suivant:\n{}".format(xelon_files))
            self.stdout.write("Nombre de relations ajoutées: {}".format(count))

        elif options['backup_insert']:
            self._insert(CorvetBackup, excel.corvet_backup_table(), "vin")

        elif options['delete']:
            Xelon.objects.all().delete()
            Corvet.objects.all().delete()
            Corvet.xelons.through.objects.all().delete()
            CorvetBackup.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Xelon, Corvet, CorvetBackup, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Xelon", "Corvet", "CorvetBackup"]:
                self.stdout.write("Suppression des données de la table {} terminée!".format(table))

    def _insert(self, model, excel_method, columns_name):
        nb_prod_before = model.objects.count()
        for row in excel_method:
            log.info(row)
            if len(row[columns_name]):
                try:
                    m = model(**row)
                    m.save()
                except IntegrityError as err:
                    log.warning("IntegrityError:{}".format(err))
        nb_prod_after = model.objects.count()
        self.stdout.write("Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
        self.stdout.write("Nombre de produits total :      {}".format(nb_prod_after))
