import logging
from django.core.management.base import BaseCommand
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db.utils import IntegrityError, DataError
from django.core.management import call_command
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from squalaetp.models import Xelon
from psa.models import Corvet
from utils.conf import XLS_SQUALAETP_FILE, XLS_DELAY_FILES
from utils.django.models import defaults_dict

from ._excel_squalaetp import ExcelSqualaetp
from ._excel_delay_analysis import ExcelDelayAnalysis

logger = logging.getLogger('command')


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
            '--xelon_update',
            action='store_true',
            dest='xelon_update',
            help='Update Xelon table',
        )
        parser.add_argument(
            '--relations',
            action='store_true',
            dest='relations',
            help='add the relationship between the xelon and corvet tables',
        )

    def handle(self, *args, **options):
        self.stdout.write("[SQUALAETP] Waiting...")

        if options['xelon_update']:
            if options['filename'] is not None:
                squalaetp = ExcelSqualaetp(options['filename'])
            else:
                squalaetp = ExcelSqualaetp(XLS_SQUALAETP_FILE)

            self._squalaetp_file(Xelon, squalaetp)
            self._delay_files(Xelon, squalaetp)

        elif options['relations']:
            self._foreignkey_relation()

        else:
            call_command("loadraspeedi")
            call_command("programing")
            # call_command("corvet")
            call_command("loadsqualaetp", "--xelon_update")
            call_command("indicator")
            call_command("importcorvet", "--squalaetp")
            call_command("exportsqualaetp")
            self._foreignkey_relation()

    def _foreignkey_relation(self):
        self.stdout.write("[SQUALAETP_RELATIONSHIPS] Waiting...")

        nb_xelon, nb_corvet, objects_list = 0, 0, []
        for xelon in Xelon.objects.filter(corvet__isnull=True):
            try:
                xelon.corvet = Corvet.objects.get(pk=xelon.vin)
                xelon.save()
                nb_xelon += 1
            except ObjectDoesNotExist:
                objects_list.append(xelon.numero_de_dossier)
        self.stdout.write(
            self.style.SUCCESS(
                "[SQUALAETP] Relationships update completed: CORVET/XELON = {} | RASPEEDI/CORVET = {}".format(
                    nb_xelon, nb_corvet
                )
            )
        )

    def _squalaetp_file(self, model, excel):
        self.stdout.write("[XELON] Waiting...")
        nb_prod_before, nb_prod_update = model.objects.count(), 0
        model.objects.exclude(numero_de_dossier__in=list(excel.sheet['numero_de_dossier'])).update(is_active=False)
        for row in excel.xelon_table():
            xelon_number = row.get("numero_de_dossier")
            defaults = defaults_dict(model, row, "numero_de_dossier")
            try:
                action_filter = Q(content__startswith='OLD_VIN') | Q(content__startswith='OLD_PROD')
                queryset = model.objects.filter(numero_de_dossier=xelon_number, actions__isnull=False).first()
                if queryset and queryset.actions.filter(action_filter):
                    self.stdout.write(f"[XELON] Xelon file {xelon_number} not modified")
                    continue
                obj, created = model.objects.update_or_create(numero_de_dossier=xelon_number, defaults=defaults)
                if not created:
                    nb_prod_update += 1
            except IntegrityError as err:
                logger.error(f"[XELON_CMD] IntegrityError: {xelon_number} -{err}")
            except DataError as err:
                logger.error(f"[XELON_CMD] DataError: {xelon_number} - {err}")
        model.objects.filter(numero_de_dossier__in=list(excel.sheet['numero_de_dossier'])).update(is_active=True)
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[XELON] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                )
            )
        )

    def _delay_files(self, model, squalaetp):
        self.stdout.write("[DELAY] Waiting...")
        nb_prod_before, nb_prod_update = model.objects.count(), 0
        try:
            excel = ExcelDelayAnalysis(XLS_DELAY_FILES)
            xelon_list, delay_list = list(squalaetp.sheet['numero_de_dossier']), list(excel.sheet['n_de_dossier'])
            self.stdout.write(f"[DELAY] Nb dossiers xelon: {len(xelon_list)} - Nb dossiers delais: {len(delay_list)}")
            model.objects.exclude(Q(numero_de_dossier__in=delay_list) |
                                  Q(type_de_cloture__in=['Réparé', 'Rebut', 'N/A']) |
                                  Q(date_retour__isnull=True)).update(type_de_cloture='N/A')
            for row in excel.table():
                xelon_number = row.get("numero_de_dossier")
                product_model = row.get("modele_produit")
                defaults = defaults_dict(model, row, "numero_de_dossier", "modele_produit")
                try:
                    obj, created = model.objects.update_or_create(numero_de_dossier=xelon_number, defaults=defaults)
                    if not created:
                        nb_prod_update += 1
                    if product_model and not obj.modele_produit:
                        obj.modele_produit = product_model
                        obj.save()
                except IntegrityError as err:
                    logger.error(f"[DELAY_CMD] IntegrityError row {xelon_number} : {err}")
                except DataError as err:
                    logger.error(f"[DELAY_CMD] DataError row {xelon_number} : {err}")
                except FieldDoesNotExist as err:
                    logger.error(f"[DELAY_CMD] FieldDoesNotExist row {xelon_number} : {err}")
                except KeyError as err:
                    logger.error(f"[DELAY_CMD] KeyError row {xelon_number} : {err}")
                except ValidationError as err:
                    logger.error(f"[DELAY_CMD] ValidationError {xelon_number} : {err}")

            nb_prod_after = model.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "[DELAY] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                    )
                )
            )
        except ValueError as err:
            logger.error(f"[DELAY_CMD] ValueError: {err}")
