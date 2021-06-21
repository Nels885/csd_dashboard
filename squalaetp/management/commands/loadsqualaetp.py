import logging
from django.core.management.base import BaseCommand
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db.utils import IntegrityError, DataError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

from squalaetp.models import Xelon, ProductCategory, Indicator
from psa.models import Corvet
from utils.conf import XLS_SQUALAETP_FILE, XLS_DELAY_FILES, string_to_list
from utils.django.models import defaults_dict
from utils.data.analysis import ProductAnalysis

from ._excel_squalaetp import ExcelSqualaetp
from ._excel_delay_analysis import ExcelDelayAnalysis

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Squalaetp tables in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-S',
            '--squalaetp_file',
            dest='squalaetp_file',
            help='Specify import Excel Squalaetp file',
        )
        parser.add_argument(
            '-D',
            '--delay_files',
            dest='delay_files',
            help='Specify import Excel Delay files',
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
            help='Add the relationship between the xelon and corvet tables',
        )
        parser.add_argument(
            '--prod_category',
            action='store_true',
            dest='prod_category',
            help='Add values in ProductCategory table',
        )

    def handle(self, *args, **options):
        self.stdout.write("[SQUALAETP] Waiting...")

        if options['xelon_update']:
            if options['squalaetp_file'] is not None:
                squalaetp = ExcelSqualaetp(options['squalaetp_file'])
            else:
                squalaetp = ExcelSqualaetp(XLS_SQUALAETP_FILE)
            if options['delay_files']:
                delay_list = string_to_list(options['delay_files'])
                delay = ExcelDelayAnalysis(delay_list)
            else:
                delay = ExcelDelayAnalysis(XLS_DELAY_FILES)

            self._squalaetp_file(Xelon, squalaetp)
            self._delay_files(Xelon, squalaetp, delay)
            self._indicator()

        elif options['relations']:
            self._foreignkey_relation()

        elif options['prod_category']:
            self._product_category()

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
        if not excel.ERROR:
            model.objects.exclude(numero_de_dossier__in=excel.xelon_number_list()).update(is_active=False)
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
        else:
            self.stdout.write(self.style.WARNING("[XELON] No squalaetp file found"))

    def _delay_files(self, model, squalaetp, delay):
        self.stdout.write("[DELAY] Waiting...")
        nb_prod_before, nb_prod_update, value_error_list = model.objects.count(), 0, []
        xelon_list, delay_list = squalaetp.xelon_number_list(), delay.xelon_number_list()
        if not delay.ERROR:
            self.stdout.write(f"[DELAY] Nb dossiers xelon: {len(xelon_list)} - Nb dossiers delais: {len(delay_list)}")
            model.objects.exclude(Q(numero_de_dossier__in=delay_list) |
                                  Q(type_de_cloture__in=['Réparé', 'Rebut', 'N/A']) |
                                  Q(date_retour__isnull=True)).update(type_de_cloture='N/A')
            for row in delay.table():
                xelon_number = row.get("numero_de_dossier")
                product_model = row.get("modele_produit")
                defaults = defaults_dict(model, row, "numero_de_dossier", "modele_produit")
                try:
                    ProductCategory.objects.get_or_create(
                        product_model=product_model, defaults={'category': 'DEFAUT'})
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
                except ValueError:
                    value_error_list.append(xelon_number)
            if value_error_list:
                logger.error(f"[DELAY_CMD] ValueError row: {', '.join(value_error_list)}")

            nb_prod_after = model.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "[DELAY] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        delay.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                    )
                )
            )
        else:
            self.stdout.write(self.style.WARNING("[DELAY] No delay files found"))

    def _product_category(self):
        xelons = Xelon.objects.exclude(modele_produit="")
        psa = xelons.filter(Q(ilot='PSA') | Q(famille_produit__exact='TBORD PSA')).exclude(famille_produit='CALC MOT')
        clarion = xelons.filter(ilot='CLARION')
        etude = xelons.filter(ilot='LaboQual').exclude(famille_produit='CALC MOT')
        autre = xelons.filter(ilot='ILOTAUTRE').exclude(Q(famille_produit='CALC MOT') |
                                                        Q(famille_produit__exact='TBORD PSA'))
        calc_mot = xelons.filter(famille_produit='CALC MOT')
        defaut = xelons.filter(ilot='DEFAUT').exclude(famille_produit='CALC MOT')

        cat_list = [
            (psa, "PSA"), (clarion, "CLARION"), (etude, "ETUDE"), (autre, "AUTRE"), (calc_mot, "CALCULATEUR"),
            (defaut, "DEFAUT")
        ]

        cat_old = ProductCategory.objects.count()

        for model, category in cat_list:
            values_list = list(model.values_list('modele_produit').distinct())
            values_list = list(set(values_list))

            for prod in values_list:
                ProductCategory.objects.get_or_create(product_model=prod[0], defaults={'category': category})

        cat_new = ProductCategory.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"[SQUALAETP] ProductCategory update completed: ADD = {cat_new - cat_old}"
            )
        )

    def _indicator(self):
        self.stdout.write("[INDICATOR] Waiting...")

        prod = ProductAnalysis()
        defaults = {
            "products_to_repair": prod.pending,
            "express_products": prod.express,
            "late_products": prod.late,
            "output_products": 0,
        }
        obj, created = Indicator.objects.update_or_create(date=timezone.now(), defaults=defaults)
        for query in prod.pendingQueryset:
            obj.xelons.add(query)
        self.stdout.write(self.style.SUCCESS("[INDICATOR] data update completed"))
