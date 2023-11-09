import logging
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError, DataError

from psa.models import DefaultCode
from utils.django.models import defaults_dict

from ._excel_psa import ExcelDefaultCode

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the DefaultCode table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )

    def handle(self, *args, **options):
        self.stdout.write("[DEFAULT_CODE_CMD] Waiting...")

        if options['filename'] is not None:
            excel = ExcelDefaultCode(options['filename'])
            if self._update_or_create(DefaultCode, excel):
                self.stdout.write(self.style.WARNING("[CORVET_CMD] No squalaetp file found"))

    def _update_or_create(self, model, excel):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        if not excel.ERROR:
            for row in excel.read():
                logger.info(row)
                code = row.pop('code')
                ecu_type = row.pop('ecu_type')
                type = row.get('type', '')
                try:
                    defaults = defaults_dict(model, row, 'code', 'type', 'ecu_type')
                    obj, created = model.objects.update_or_create(
                        code=code, type=type, ecu_type=ecu_type, defaults=defaults
                    )
                    if not created:
                        nb_prod_update += 1
                except KeyError as err:
                    logger.error(f"[DEFAULT_CODE_CMD] KeyError: {code} {type} {ecu_type} - {err}")
                except IntegrityError as err:
                    logger.error(f"[DEFAULT_CODE_CMD] IntegrityError: {code} {type} {ecu_type} - {err}")
                except ValidationError as err:
                    logger.error(f"[DEFAULT_CODE_CMD] ValidationError: {code} {type} {ecu_type} - {err}")
                except DataError as err:
                    logger.error(f"[DEFAULT_CODE_CMD] DataError {code} {type} {ecu_type} - {err}")
            nb_prod_after = model.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "[DEFAULT_CODE_CMD] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                    )
                )
            )
        return excel.ERROR
