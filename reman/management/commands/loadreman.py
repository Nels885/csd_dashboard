import logging
from django.core.management.base import BaseCommand
from django.db.utils import DataError, IntegrityError

from reman.models import EcuRefBase, EcuModel, EcuType
from utils.django.models import defaults_dict

from ._excel_sem_reman import ExcelSemRefBase

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the SemRefBase table in the database'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            '-s',
            '--sheet_id',
            type=int,
            default=0
        )
        parser.add_argument(
            '-f',
            '--file',
            dest='filename',
            help='Specify import Excel file',
        )
        parser.add_argument(
            '--sem',
            action='store_true',
            dest='sem',
            help='Add SEM data',
        )

    def handle(self, *args, **options):
        if options['sem'] and options['filename'] is not None:
            self.stdout.write("[SEMREFBASE] Waiting...")
            extraction = ExcelSemRefBase(options['filename'], sheet_name=options['sheet_id'])
            self._sem_update(extraction.read_all())

    def _sem_update(self, data):
        nb_base_before, nb_ecu_before = EcuRefBase.objects.count(), EcuModel.objects.count()
        nb_type_before = EcuType.objects.count()
        nb_base_update, nb_ecu_update, nb_type_update = 0, 0, 0
        for row in data:
            logger.info(row)
            reman_reference = type_obj = None
            try:
                reman_reference = row.get("reman_reference")

                # Update or Create SemType
                if row.get('hw_reference'):
                    type_values = defaults_dict(EcuType, row, "hw_reference")
                    type_values.update({'hw_type': 'NAV', 'technical_data': 'SEM', 'supplier_oe': 'PARROT'})
                    type_obj, type_created = EcuType.objects.update_or_create(
                        hw_reference=row.get('hw_reference'), defaults=type_values)
                    if not type_created:
                        nb_type_update += 1

                # Update or Create SemModel
                if row.get('barcode'):
                    sem_model_values = defaults_dict(EcuModel, row, "barcode")
                    sem_model_values['ecu_type'] = type_obj
                    ecu_obj, ecu_created = EcuModel.objects.update_or_create(
                        barcode=row['barcode'], defaults=sem_model_values
                    )
                    if not ecu_created:
                        nb_ecu_update += 1

                # Update or Create SemRefBase
                if reman_reference:
                    base_values = defaults_dict(EcuRefBase, row, "reman_reference")
                    base_values['ecu_type'] = type_obj
                    base_obj, base_created = EcuRefBase.objects.update_or_create(
                        reman_reference=reman_reference, defaults=base_values
                    )
                    if not base_created:
                        nb_base_update += 1
            except KeyError as err:
                logger.error(f"[ECUREBASE_CMD] KeyError: {reman_reference} - {err}")
            except DataError as err:
                logger.error(f"[ECUREFBASE_CMD] DataError: {reman_reference} - {err}")
            except IntegrityError as err:
                logger.error(f"[ECUREFBASE_CMD] IntegrityError: {reman_reference} - {err}")

        nb_base_after, nb_ecu_after = EcuRefBase.objects.count(), EcuModel.objects.count()
        nb_type_after = EcuType.objects.count()
        self._end_message("ECUTYPE", data, nb_type_update, nb_type_after, nb_type_before)
        self._end_message("ECUMODEL", data, nb_ecu_update, nb_ecu_after, nb_ecu_before)
        self._end_message("ECUREFBASE", data, nb_base_update, nb_base_after, nb_base_before)

    def _end_message(self, title, data, nb_update, nb_after, nb_before):
        self.stdout.write(
            self.style.SUCCESS(
                "[{}] Data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    title, len(data), nb_after - nb_before, nb_update, nb_after
                )
            )
        )
