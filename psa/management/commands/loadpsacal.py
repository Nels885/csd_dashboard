import logging
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError, DataError

from psa.models import Calibration
from utils.django.models import defaults_dict

from ._excel_psa import ExcelNacCalibration

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Calibration table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )

    def handle(self, *args, **options):
        self.stdout.write("[CAL_CMD] Waiting...")

        if options['filename'] is not None:
            excel = ExcelNacCalibration(options['filename'])
            if self._update_or_create(Calibration, excel):
                self.stdout.write(self.style.WARNING("[CAL_CMD] No Excel file found"))

    def _update_or_create(self, model, excel):
        nb_prod_before = model.objects.count()
        nb_prod_update = 0
        if not excel.ERROR:
            for row in excel.read():
                logger.info(row)
                factory = row.pop('factory')
                try:
                    defaults = defaults_dict(model, row, 'factory')
                    obj, created = model.objects.update_or_create(factory=factory, defaults=defaults)
                    if not created:
                        nb_prod_update += 1
                except KeyError as err:
                    logger.error(f"[CAL_CMD] KeyError: {factory} - {err}")
                except IntegrityError as err:
                    logger.error(f"[CAL_CMD] IntegrityError: {factory} - {err}")
                except ValidationError as err:
                    logger.error(f"[CAL_CMD] ValidationError: {factory} - {err}")
                except DataError as err:
                    logger.error(f"[CAL_CMD] DataError {factory} - {err}")
            nb_prod_after = model.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    "[CAL_CMD] data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                        excel.nrows, nb_prod_after - nb_prod_before, nb_prod_update, nb_prod_after
                    )
                )
            )
        return excel.ERROR
