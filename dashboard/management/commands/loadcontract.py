import logging
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError, DataError

from dashboard.models import Contract
from utils.django.models import defaults_dict

from ._excel_contract import ExcelContract

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the Contract table in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import EXCEL file',
        )

    def handle(self, *args, **options):
        self.stdout.write("[CONTRACT] Waiting...")

        if options['filename'] is not None:
            excel = ExcelContract(options['filename'])
            nb_before = Contract.objects.count()
            nb_update = 0
            if not excel.ERROR:
                for row in excel.read():
                    logger.info(row)
                    pk = row.pop("id")
                    try:
                        defaults = defaults_dict(Contract, row, "id")
                        obj, created = Contract.objects.update_or_create(pk=pk, defaults=defaults)
                        if not created:
                            nb_update += 1
                    except IntegrityError as err:
                        logger.error(f"[CONTRACT_CMD] IntegrityError: {pk} - {err}")
                    except Contract.MultipleObjectsReturned as err:
                        logger.error(f"[CONTRACT_CMD] MultipleObjectsReturned: {pk} - {err}")
                    except DataError as err:
                        logger.error(f"[CONTRACT_CMD] DataError: {pk} - {err}")
                    except ValidationError as err:
                        logger.error(f"[CONTRACT_CMD] ValidationError: {pk} - {err}")
                nb_after = Contract.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[CONTRACT] Data update completed: EXCEL_LINES = {excel.nrows} | ADD = " +
                        f"{nb_after - nb_before} | UPDATE = {nb_update} | TOTAL = {nb_after}"
                    )
                )
            else:
                self.stdout.write(self.style.WARNING("[CONTRACT] No excel file found"))
        else:
            self.stdout.write(self.style.WARNING("[CONTRACT] Path to excel file missing !"))
