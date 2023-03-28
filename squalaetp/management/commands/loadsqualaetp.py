import logging
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from squalaetp.models import Xelon, ProductCategory, Indicator
from psa.models import Multimedia, Ecu
from utils.conf import XLS_SQUALAETP_FILE, XLS_DELAY_FILES, XLS_TIME_LIMIT_FILE, string_to_list
from utils.django.models import defaults_dict
from utils.django.validators import comp_ref_isvalid
from utils.data.analysis import ProductAnalysis

from ._excel_squalaetp import ExcelSqualaetp
from ._excel_analysis import ExcelDelayAnalysis, ExcelTimeLimitAnalysis

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Squalaetp tables in the database'
    MAX_SIZE = None

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
            '-T',
            '--time_limit_file',
            dest='time_limit_file',
            help='Specify import Excel Time Limit file',
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
        parser.add_argument(
            '--xelon_name_update',
            action='store_true',
            dest='xelon_name',
            help='Update Xelon name'
        )

    def handle(self, *args, **options):
        if options['squalaetp_file'] is not None:
            squalaetp = ExcelSqualaetp(options['squalaetp_file'])
        else:
            squalaetp = ExcelSqualaetp(XLS_SQUALAETP_FILE)
        if options['delay_files']:
            delay_files = string_to_list(options['delay_files'])
        else:
            delay_files = XLS_DELAY_FILES

        if options['time_limit_file']:
            time_limit = ExcelTimeLimitAnalysis(options['time_limit_file'])
        else:
            time_limit = ExcelTimeLimitAnalysis(XLS_TIME_LIMIT_FILE)
        self._squalaetp_file(Xelon, squalaetp)
        self._delay_files(Xelon, squalaetp, delay_files)
        self._time_limit_files(Xelon, squalaetp, time_limit)
        self._indicator()

        if options['relations']:
            self._foreignkey_relation()
        if options['prod_category']:
            self._product_category()
        if options['xelon_name']:
            self._xelon_name_update()

    def _foreignkey_relation(self):
        self.stdout.write("[SQUALAETP_RELATIONSHIPS] Waiting...")

        nb_xelon, nb_category = 0, 0
        for xelon in Xelon.objects.filter(corvet__isnull=True):
            xelon.save()
            nb_xelon += 1
        self.stdout.write(
            self.style.SUCCESS("[SQUALAETP] Relationships update completed: CORVET/XELON = {}".format(nb_xelon))
        )
        for xelon in Xelon.objects.filter(product__isnull=True):
            xelon.save()
            nb_category += 1
        self.stdout.write(
            self.style.SUCCESS("[SQUALAETP] Relationships update completed: CATEGORY/XELON = {}".format(nb_category))
        )

    def _squalaetp_file(self, model, excel):
        self.stdout.write("[SQUALAETP] Waiting...")
        nb_prod_before, nb_prod_update = model.objects.count(), 0
        nb_category_change = 0
        if not excel.ERROR:
            model.objects.exclude(Q(numero_de_dossier__in=excel.xelon_number_list()) |
                                  Q(type_de_cloture__in=['Réparé', 'Rebut', 'N/A']) |
                                  Q(date_retour__isnull=True)).update(type_de_cloture='N/A', is_active=False)
            for row in excel.read({'is_active': True}):
                xelon_number = row.get("numero_de_dossier")
                defaults = defaults_dict(model, row, "numero_de_dossier")
                try:
                    if self._actions_check(xelon_number):
                        self.stdout.write(f"[SQUALAETP] Xelon file {xelon_number} not modified")
                        continue
                    obj, created = model.objects.update_or_create(numero_de_dossier=xelon_number, defaults=defaults)
                    if not created:
                        nb_prod_update += 1
                    if "ZONECE" in obj.lieu_de_stockage and obj.product.animator is None:
                        obj.product.category = "ETUDE"
                        obj.product.save()
                        nb_category_change += 1
                except Exception as err:
                    logger.error(f"[SQUALAETP_CMD] {xelon_number} - {err}")
            model.objects.exclude(numero_de_dossier__in=excel.xelon_number_list()).update(is_active=False)
            nb_prod_after = model.objects.count()
            self.stdout.write(f"[SQUALAETP_FILE] '{XLS_SQUALAETP_FILE}' => OK")
            self.stdout.write(self.style.SUCCESS(f"[SQUALAETP] Product category changed: {nb_category_change}"))
            self.stdout.write(
                self.style.SUCCESS(
                    "[SQUALAETP] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                    )
                )
            )
        else:
            self.stdout.write(f"[SQUALAETP_FILE] {excel.ERROR}")

    @classmethod
    def _actions_check(cls, xelon_number):
        action_filter = Q(content__startswith='OLD_VIN') | Q(content__startswith='OLD_PROD')
        query = Xelon.objects.filter(numero_de_dossier=xelon_number, actions__isnull=False).first()
        if query and query.actions.filter(action_filter):
            return True
        return False

    def _delay_files(self, model, squalaetp, delay_files):
        self.stdout.write("[DELAY] Waiting...")
        nb_prod_before, nb_prod_update, nrows, value_error_list = model.objects.count(), 0, 0, []
        xelon_list, delay_list = squalaetp.xelon_number_list(), []
        for count, file in enumerate(delay_files):
            if count == 0:
                delay = ExcelDelayAnalysis(file, datedelta=0)
            else:
                delay = ExcelDelayAnalysis(file)
            if not delay.ERROR:
                delay_list += delay.xelon_number_list()
                for row in delay.table():
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
                    except ValueError:
                        value_error_list.append(xelon_number)
                    except Exception as err:
                        logger.error(f"[DELAY_CMD] {xelon_number} - {err}")
                if value_error_list:
                    logger.error(f"[DELAY_CMD] ValueError row: {', '.join(value_error_list)}")

                self.stdout.write(f"[DELAY_FILE] '{file}' => OK")
                nrows += delay.nrows
            else:
                self.stdout.write(f"[DELAY_FILE] {delay.ERROR}")
        nb_prod_after = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"[DELAY_CMD] data update completed: EXCEL_LINES = {nrows} | " +
                f"ADD = {nb_prod_after - nb_prod_before} | UPDATE = {nb_prod_update} | TOTAL = {nb_prod_after}"
            )
        )
        self.stdout.write(f"[DELAY] Nb dossiers xelon: {len(xelon_list)} - Nb dossiers delais: {len(delay_list)}")

    def _time_limit_files(self, model, squalaetp, excel):
        self.stdout.write("[TIME_LIMIT] Waiting...")
        nb_prod_before, nb_prod_update, value_error_list = model.objects.count(), 0, []
        if not excel.ERROR:
            for row in excel.read_all():
                xelon_number = row.get("numero_de_dossier")
                defaults = defaults_dict(model, row, "numero_de_dossier")
                try:
                    obj, created = model.objects.update_or_create(numero_de_dossier=xelon_number, defaults=defaults)
                    if not created:
                        nb_prod_update += 1
                except ValueError:
                    value_error_list.append(xelon_number)
                except Exception as err:
                    logger.error(f"[TIME_LIMIT_CMD] {xelon_number} - {err}")
            if value_error_list:
                logger.error(f"[TIME_LIMIT_CMD] ValueError row: {', '.join(value_error_list)}")

            nb_prod_after = model.objects.count()
            self.stdout.write(f"[TIME_LIMIT_FILE] '{XLS_TIME_LIMIT_FILE}' => OK")
            self.stdout.write(
                self.style.SUCCESS(
                    "[TIME_LIMIT] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                    )
                )
            )
        else:
            self.stdout.write(f"[TIME_LIMIT_FILE] {excel.ERROR}")

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
            self.style.SUCCESS(f"[SQUALAETP] ProductCategory update completed: ADD = {cat_new - cat_old}")
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

    def _xelon_name_update(self):
        self.stdout.write("[ECU & MEDIA] Waiting...")
        xelons = Xelon.objects.filter(
            corvet__isnull=False, product__isnull=False, date_retour__isnull=False).order_by('date_retour')
        self.MAX_SIZE, number = xelons.count(), 0
        for xelon in xelons:
            corvet, product = xelon.corvet, xelon.product
            if corvet and product:
                ecu_dict = {
                    "NAV": corvet.electronique_14x, "RAD": corvet.electronique_14f,
                    "EMF": corvet.electronique_14l, "CMB": corvet.electronique_14k, "BSI": corvet.electronique_14b,
                    "CMM": corvet.electronique_14a, "HDC": corvet.electronique_16p, "BSM": corvet.electronique_16b
                }
                for corvet_type, comp_ref in ecu_dict.items():
                    if product.corvet_type == corvet_type and comp_ref_isvalid(comp_ref):
                        if product.corvet_type in ["NAV", "RAD"]:
                            obj, created = Multimedia.objects.update_or_create(
                                hw_reference=comp_ref,
                                defaults={'xelon_name': xelon.modele_produit, 'type': product.corvet_type})
                        else:
                            obj, created = Ecu.objects.update_or_create(
                                comp_ref=comp_ref,
                                defaults={'xelon_name': xelon.modele_produit, 'type': product.corvet_type}
                            )
                        break
            if number % 100 == 1:
                self._progress_bar(number)
            number += 1
        self.stdout.write(self.style.SUCCESS(f"\r\n[ECU & MEDIA] data update completed: NB_UPDATE={self.MAX_SIZE}"))

    def _progress_bar(self, current_size, bar_length=80):
        if self.MAX_SIZE is not None:
            percent = float(current_size) / self.MAX_SIZE
            arrow = '-' * int(round(percent*bar_length) - 1) + '>'
            spaces = ' ' * (bar_length - len(arrow))
            print("\r[{0}]{1}% ".format(arrow + spaces, int(round(percent*100))), end="", flush=True)
