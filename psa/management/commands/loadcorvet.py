import logging
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError, DataError
from django.db.models import Q

from psa.models import Corvet, CorvetAttribute
from utils.conf import XLS_SQUALAETP_FILE, XLS_ATTRIBUTS_FILE
from utils.django.models import defaults_dict

from ._csv_squalaetp_corvet import CsvCorvet
from ._excel_psa import ExcelCorvet, ExcelCorvetAttribute

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Corvet table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )
        parser.add_argument(
            '--import_csv',
            action='store_true',
            dest='import_csv',
            help='import Corvet CSV file',
        )
        parser.add_argument(
            '--attribute',
            action='store_true',
            dest='attribute',
            help='import Corvet attribute file',
        )
        parser.add_argument(
            '--relations',
            action='store_true',
            dest='relations',
            help='add the relationship between the corvet and multimedia tables',
        )

    def handle(self, *args, **options):
        self.stdout.write("[CORVET_CMD] Waiting...")

        if options['import_csv']:
            if options['filename'] is not None:
                excel = CsvCorvet(options['filename'])
                if self._update_or_create(Corvet, excel):
                    self.stdout.write(self.style.WARNING("[CORVET_CMD] No CSV file found"))
            else:
                self.stdout.write(self.style.WARNING("[CORVET_CMD] Missing CSV file"))

        elif options['relations']:
            self._foreignkey_relation()

        elif options['attribute']:
            if options['filename'] is not None:
                excel = ExcelCorvetAttribute(options['filename'])
            else:
                excel = ExcelCorvetAttribute(XLS_ATTRIBUTS_FILE)

            if self._corvet_attribute(CorvetAttribute, excel):
                self.stdout.write(self.style.WARNING("[CORVET_CMD] No Attribute file found"))
        else:
            if options['filename'] is not None:
                excel = ExcelCorvet(options['filename'], XLS_ATTRIBUTS_FILE)
            else:
                excel = ExcelCorvet(XLS_SQUALAETP_FILE, XLS_ATTRIBUTS_FILE)

            if self._update_or_create(Corvet, excel):
                self.stdout.write(self.style.WARNING("[CORVET_CMD] No squalaetp file found"))

    def _foreignkey_relation(self):
        self.stdout.write("[CORVET_RELATIONSHIPS] Waiting...")
        corvets = Corvet.objects.filter(
            Q(prods__btel__isnull=True, prods__radio__isnull=True) | Q(prods__bsi__isnull=True) |
            Q(prods__emf__isnull=True) | Q(prods__cmb__isnull=True) | Q(prods__cmm__isnull=True) |
            Q(prods__bsm__isnull=True) | Q(prods__hdc__isnull=True)
        )
        for corvet in corvets:
            corvet.save()
        self.stdout.write(
            self.style.SUCCESS(
                "[CORVET_CMD] Relationships update completed: CORVET/MULTIMEDIA = {}".format(corvets.count())
            )
        )

    def _update_or_create(self, model, excel):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        if not excel.ERROR:
            for row in excel.read():
                logger.info(row)
                vin = row.pop('vin')
                try:
                    defaults = defaults_dict(model, row, 'vin')
                    obj, created = model.objects.update_or_create(
                        vin=vin, defaults=defaults
                    )
                    if not created:
                        nb_prod_update += 1
                except KeyError as err:
                    logger.error(f"[CORVET_CMD] KeyError: {vin} - {err}")
                except IntegrityError as err:
                    logger.error(f"[CORVET_CMD] IntegrityError: {vin} - {err}")
                except ValidationError as err:
                    logger.error(f"[CORVET_CMD] ValidationError: {vin} - {err}")
            nb_prod_after = model.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "[CORVET_CMD] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                    )
                )
            )
        return excel.ERROR

    def _corvet_attribute(self, model, excel):
        nb_before = model.objects.count()
        nb_update = 0
        if not excel.ERROR:
            for row in excel.read():
                logger.info(row)
                pk = row.pop("id")
                try:
                    defaults = defaults_dict(model, row, "id")
                    obj, created = model.objects.update_or_create(pk=pk, defaults=defaults)
                    if not created:
                        nb_update += 1
                except IntegrityError as err:
                    logger.error(f"[CORVET_ATTRIBUTE_CMD] IntegrityError: {pk} - {err}")
                except model.MultipleObjectsReturned as err:
                    logger.error(f"[CORVET_ATTRIBUTE_CMD] MultipleObjectsReturned: {pk} - {err}")
                except DataError as err:
                    logger.error(f"[CORVET_ATTRIBUTE_CMD] DataError: {pk} - {err}")
                except ValidationError as err:
                    logger.error(f"[CORVET_ATTRIBUTE_CMD] ValidationError: {pk} - {err}")
            nb_after = model.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"[CORVET_ATTRIBUTE_CMD] Data update completed: EXCEL_LINES = {excel.nrows} | " +
                    f"ADD = {nb_after - nb_before} | UPDATE = {nb_update} | TOTAL = {nb_after}"
                )
            )
        return excel.ERROR
