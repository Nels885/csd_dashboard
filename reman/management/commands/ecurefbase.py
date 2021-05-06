import logging
from django.core.management.base import BaseCommand
from django.db.utils import DataError, IntegrityError

from reman.models import EcuRefBase, EcuModel, EcuType, SparePart
from utils.conf import XLS_ECU_REF_BASE, CSD_ROOT, conf
from utils.file.export import ExportExcel, os
from utils.django.models import defaults_dict

from ._excel_reman import ExcelEcuRefBase

logger = logging.getLogger('command')


class Command(BaseCommand):
    help = 'Interact with the EcuRefBase table in the database'

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
            '--export',
            action='store_true',
            dest='export',
            help='Export all data of EcuRefBase',
        )

    def handle(self, *args, **options):
        self.stdout.write("[ECUREFBASE] Waiting...")

        if options['export']:
            self._export()
        else:
            if options['filename'] is not None:
                extraction = ExcelEcuRefBase(options['filename'], sheet_name=options['sheet_id'])
            else:
                extraction = ExcelEcuRefBase(XLS_ECU_REF_BASE, sheet_name=options['sheet_id'])
            self._update_or_create(extraction.read_all())

    def _update_or_create(self, data):

        nb_base_before, nb_ecu_before = EcuRefBase.objects.count(), EcuModel.objects.count()
        nb_type_before = EcuType.objects.count()
        nb_base_update, nb_ecu_update, nb_type_update, nb_part_create = 0, 0, 0, 0
        for row in data:
            logger.info(row)
            code_produit = reman_reference = type_obj = None
            try:
                code_produit, reman_reference = row["code_produit"], row["reman_reference"]

                # Update or create SpareParts
                part_obj, part_created = SparePart.objects.get_or_create(
                     code_produit=code_produit, code_magasin="MAGREM PSA", code_zone="REMAN PSA")
                if part_created:
                    nb_part_create += 1

                # Update or Create EcuType
                if row['technical_data']:
                    type_values = defaults_dict(EcuType, row, "hw_reference", "technical_data")
                    type_values['spare_part'] = part_obj
                    type_obj, type_created = EcuType.objects.update_or_create(
                        hw_reference=row['hw_reference'], technical_data=row['technical_data'], defaults=type_values
                    )
                    if not type_created:
                        nb_type_update += 1

                # Update or Create Ecumodel
                if row['psa_barcode']:
                    ecu_model_values = defaults_dict(EcuModel, row, "psa_barcode")
                    ecu_model_values['ecu_type'] = type_obj
                    ecu_obj, ecu_created = EcuModel.objects.update_or_create(
                        psa_barcode=row['psa_barcode'], defaults=ecu_model_values
                    )
                    if not ecu_created:
                        nb_ecu_update += 1

                # Update or Create EcurefBase
                if reman_reference:
                    base_values = defaults_dict(EcuRefBase, row, "reman_reference")
                    base_values['ecu_type'] = type_obj
                    base_obj, base_created = EcuRefBase.objects.update_or_create(
                        reman_reference=reman_reference, defaults=base_values
                    )
                    if not base_created:
                        nb_base_update += 1
            except KeyError as err:
                logger.error(f"[ECUREBASE_CMD] KeyError: {err}")
            except DataError as err:
                logger.error(f"[ECUREFBASE_CMD] DataError: {reman_reference} - {err}")
            except IntegrityError as err:
                logger.error(f"[ECUREFBASE_CMD] IntegrityError: {reman_reference} - {err}")
            except SparePart.MultipleObjectsReturned as err:
                logger.error(f"[ECUREFBASE_CMD] MultipleObjectsReturned: {code_produit} - {err}")

        nb_base_after, nb_ecu_after = EcuRefBase.objects.count(), EcuModel.objects.count()
        nb_type_after, nb_part_after = EcuType.objects.count(), SparePart.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                "[SPAREPART] Data update completed: EXCEL_LINES = {} | ADD = {} | TOTAL = {}".format(
                    len(data), nb_part_create, nb_part_after
                )
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "[ECUTYPE] Data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    len(data), nb_type_after - nb_type_before, nb_type_update, nb_type_after
                )
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "[ECUMODEL] Data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    len(data), nb_ecu_after - nb_ecu_before, nb_ecu_update, nb_ecu_after
                )
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "[ECUREFBASE] Data update completed: EXCEL_LINES = {} | ADD = {} | UPDATE = {} | TOTAL = {}".format(
                    len(data), nb_base_after - nb_base_before, nb_base_update, nb_base_after
                )
            )
        )

    def _export(self):
        filename = 'base_ref_reman_new'
        path = os.path.join(CSD_ROOT, conf.EXPORT_PATH)
        header = [
            'Reference OE', 'REFERENCE REMAN', 'Module Moteur', 'Réf HW', 'FNR', 'CODE BARRE PSA', 'REF FNR',
            'REF CAL OUT', 'REF à créer ', 'REF_PSA_OUT', 'OPENDIAG', 'REF_MAT', 'REF_COMP', 'CAL_KTAG', 'STATUT'
        ]
        queryset = EcuType.objects.all().order_by('ecu_ref_base__reman_reference')
        values_list = (
            'ecumodel__oe_raw_reference', 'ecu_ref_base__reman_reference', 'technical_data', 'hw_reference',
            'supplier_oe', 'ecumodel__psa_barcode', 'ecumodel__former_oe_reference', 'ref_cal_out',
            'spare_part__code_produit', 'ref_psa_out', 'open_diag', 'ref_mat', 'ref_comp', 'cal_ktag', 'status'
        )
        values_list = queryset.values_list(*values_list).distinct()
        ExportExcel(values_list=values_list, filename=filename, header=header).file(path, False)
        self.stdout.write(
            self.style.SUCCESS(
                "Export ECU_REF_BASE completed: NB_REF = {} | FILE = {}.csv".format(
                    queryset.count(), os.path.join(path, filename)
                )
            )
        )
