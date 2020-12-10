from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.core.exceptions import FieldDoesNotExist
from django.db.utils import IntegrityError, DataError
from django.db import connection

from squalaetp.models import Xelon
from utils.conf import XLS_SQUALAETP_FILE, XLS_DELAY_FILES
from utils.django.models import defaults_dict

from ._excel_squalaetp import ExcelSqualaetp
from ._excel_delay_analysis import ExcelDelayAnalysis


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

            self._squalaetp_file(Xelon, squalaetp)
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
                self.stdout.write(self.style.WARNING("Suppression des données de la table {} terminée!".format(table)))

    def _squalaetp_file(self, model, excel):
        self.stdout.write("[XELON] Waiting...")
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        for row in excel.xelon_table():
            xelon_number = row.get("numero_de_dossier")
            defaults = defaults_dict(model, row, "numero_de_dossier")
            try:
                obj, created = model.objects.update_or_create(numero_de_dossier=xelon_number, defaults=defaults)
                if not created:
                    nb_prod_update += 1
            except IntegrityError as err:
                self.stderr.write(self.style.ERROR("IntegrityError: {} -{}".format(xelon_number, err)))
            except DataError as err:
                self.stderr.write(self.style.ERROR("DataError: {} - {}".format(xelon_number, err)))
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[XELON] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )

    def _delay_files(self, model):
        self.stdout.write("[DELAY] Waiting...")
        nb_excel_lines, nb_prod_update = 0, 0
        excels = [ExcelDelayAnalysis(file) for file in XLS_DELAY_FILES]
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
                    self.stderr.write("IntegrityError:{}".format(err))
                except DataError as err:
                    self.stderr.write("DataError dossier {} : {}".format(row["numero_de_dossier"], err))
                except FieldDoesNotExist as err:
                    self.stderr.write("FieldDoesNotExist row {} : {}".format(row, err))
            nb_excel_lines += excel.nrows
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[DELAY] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    nb_excel_lines, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )

    def _fix_delay_files(self, model):
        self.stdout.write("[DELAY] Waiting...")
        nb_prod_update = 0
        excel = ExcelDelayAnalysis(XLS_DELAY_FILES)
        nb_prod_before = model.objects.count()
        model.objects.exclude(
            type_de_cloture__in=['Réparé', 'Rebut'], date_retour__isnull=True).update(type_de_cloture='Réparé')
        model.objects.filter(actions__isnull=True)
        for row in excel.table():
            xelon_number = row.get("numero_de_dossier")
            defaults = defaults_dict(model, row, "numero_de_dossier")
            try:
                obj, created = model.objects.update_or_create(numero_de_dossier=xelon_number, defaults=defaults)
                if not created:
                    if not obj.nom_technicien:
                        obj.type_de_cloture = ''
                        obj.save()
                    nb_prod_update += 1
            except IntegrityError as err:
                self.stderr.write(self.style.ERROR("IntegrityError row {} : {}".format(xelon_number, err)))
            except DataError as err:
                self.stderr.write(self.style.ERROR("DataError row {} : {}".format(xelon_number, err)))
            except FieldDoesNotExist as err:
                self.stderr.write(self.style.ERROR("FieldDoesNotExist row {} : {}".format(xelon_number, err)))
            except KeyError as err:
                self.stderr.write(self.style.ERROR("KeyError row {} : {}".format(xelon_number, err)))

        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[DELAY] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )
