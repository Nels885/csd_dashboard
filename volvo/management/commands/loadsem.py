import logging
from django.core.management.base import BaseCommand
from django.db.utils import DataError, IntegrityError

from volvo.models import SemRefBase, SemModel, SemType
from utils.conf import XLS_SEM_REF_BASE
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

    def handle(self, *args, **options):
        self.stdout.write("[SEMREFBASE] Waiting...")
        if options['filename'] is not None:
            extraction = ExcelSemRefBase(options['filename'], sheet_name=options['sheet_id'])
        else:
            extraction = ExcelSemRefBase(XLS_SEM_REF_BASE, sheet_name=options['sheet_id'])
        self._update_or_create(extraction.read_all())

    def _update_or_create(self, data):
        nb_base_before, nb_ecu_before = SemRefBase.objects.count(), SemModel.objects.count()
        nb_type_before = SemType.objects.count()
        nb_base_update, nb_ecu_update, nb_type_update = 0, 0, 0
        for row in data:
            logger.info(row)
            reman_reference = type_obj = None
            try:
                reman_reference = row.get("reman_reference")

                # Update or Create SemType
                if row.get('asm_reference'):
                    type_values = defaults_dict(SemType, row, "asm_reference")
                    type_obj, type_created = SemType.objects.update_or_create(
                        asm_reference=row.get('asm_reference'), defaults=type_values)
                    if not type_created:
                        nb_type_update += 1

                # Update or Create SemModel
                if row.get('pf_code_oe'):
                    sem_model_values = defaults_dict(SemModel, row, "pf_code_oe")
                    sem_model_values['ecu_type'] = type_obj
                    ecu_obj, ecu_created = SemModel.objects.update_or_create(
                        pf_code_oe=row['pf_code_oe'], defaults=sem_model_values
                    )
                    if not ecu_created:
                        nb_ecu_update += 1

                # Update or Create SemRefBase
                if reman_reference:
                    base_values = defaults_dict(SemRefBase, row, "reman_reference")
                    base_values['ecu_type'] = type_obj
                    base_obj, base_created = SemRefBase.objects.update_or_create(
                        reman_reference=reman_reference, defaults=base_values
                    )
                    if not base_created:
                        nb_base_update += 1
            except KeyError as err:
                logger.error(f"[SEMREBASE_CMD] KeyError: {reman_reference} - {err}")
            except DataError as err:
                logger.error(f"[SEMREFBASE_CMD] DataError: {reman_reference} - {err}")
            except IntegrityError as err:
                logger.error(f"[SEMREFBASE_CMD] IntegrityError: {reman_reference} - {err}")

        nb_base_after, nb_ecu_after = SemRefBase.objects.count(), SemModel.objects.count()
        nb_type_after = SemType.objects.count()
        self._end_message("SEMTYPE", data, nb_type_update, nb_type_after, nb_type_before)
        self._end_message("SEMMODEL", data, nb_ecu_update, nb_ecu_after, nb_ecu_before)
        self._end_message("SEMREFBASE", data, nb_base_update, nb_base_after, nb_base_before)

    def _end_message(self, title, data, nb_update, nb_after, nb_before):
        self.stdout.write(
            self.style.SUCCESS(
                "[{}] Data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    title, len(data), nb_after - nb_before, nb_update, nb_after
                )
            )
        )
