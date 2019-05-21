from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db.utils import IntegrityError, DataError
from django.db import connection
from django.conf import settings

from squalaetp.models import Xelon, CorvetBackup, Corvet

from ._excel_squalaetp import ExcelSqualaetp

import logging as log


class Command(BaseCommand):
    help = 'Interact with the Squalaetp tables in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--xelon_insert',
            action='store_true',
            dest='xelon_insert',
            help='Insert Xelon table',
        )
        parser.add_argument(
            '--corvet_insert',
            action='store_true',
            dest='corvet_insert',
            help='Insert Corvet table',
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
        excel = ExcelSqualaetp(settings.XLS_SQUALAETP_FILE)
        self.stdout.write("Nombre de ligne dans Excel:     {}".format(excel.nrows))
        self.stdout.write("Noms des colonnes:              {}".format(excel.columns))

        if options['xelon_insert']:
            nb_prod_before = Xelon.objects.count()
            for row in excel.xelon_table():
                log.info(row)
                if len(row["numero_de_dossier"]):
                    try:
                        m = Xelon(**row)
                        m.save()
                    except KeyError as err:
                        log.warning("Manque la valeur : {}".format(err))
                    except IntegrityError as err:
                        log.warning("IntegrityError:{}".format(err))
                    except DataError as err:
                        log.warning("DataError: {}".format(err))
                    except TypeError as err:
                        log.warning("TypeError: {}".format(err))
            nb_prod_after = Xelon.objects.count()
            self.stdout.write("Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
            self.stdout.write("Nombre de produits total :      {}".format(nb_prod_after))

        elif options['corvet_insert']:
            nb_prod_before = Corvet.objects.count()
            for row in excel.corvet_table(settings.XLS_ATTRIBUTS_FILE):
                print(row)
                if len(row["vin"]):
                    try:
                        m = Corvet(**row)
                        m.save()
                    except KeyError as err:
                        log.warning("Manque la valeur : {}".format(err))
                    except IntegrityError as err:
                        log.warning("IntegrityError:{}".format(err))
                    except DataError as err:
                        log.warning("DataError: {}".format(err))
                    except TypeError as err:
                        log.warning("TypeError: {}".format(err))
            nb_prod_after = Corvet.objects.count()
            self.stdout.write("Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
            self.stdout.write("Nombre de produits total :      {}".format(nb_prod_after))

        elif options['backup_insert']:
            nb_prod_before = CorvetBackup.objects.count()
            for row in excel.corvet_backup_table():
                log.info(row)
                if len(row["vin"]):
                    try:
                        m = CorvetBackup(**row)
                        m.save()
                    except KeyError as err:
                        log.warning("Manque la valeur : {}".format(err))
                    except IntegrityError as err:
                        log.warning("IntegrityError:{}".format(err))
                    except DataError as err:
                        log.warning("DataError: {}".format(err))
                    except TypeError as err:
                        log.warning("TypeError: {}".format(err))
            nb_prod_after = CorvetBackup.objects.count()
            self.stdout.write("Nombre de produits ajoutés :    {}".format(nb_prod_after - nb_prod_before))
            self.stdout.write("Nombre de produits total :      {}".format(nb_prod_after))

        elif options['delete']:
            Xelon.objects.all().delete()
            Corvet.objects.all().delete()
            CorvetBackup.objects.all().delete()

            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Xelon, Corvet, CorvetBackup, ])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
            for table in ["Xelon", "Corvet", "CorvetBackup"]:
                self.stdout.write("Suppression des données de la table {} terminée!".format(table))
