from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.core.management.base import BaseCommand

from reman.models import Batch, Repair, EcuRefBase

from utils.file.export import ExportExcel, os
from utils.conf import CSD_ROOT, conf, ROOT_PATHS
from utils.file import LogFile


class Command(BaseCommand):
    help = 'Export CSV file for Batch REMAN'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch',
            action='store_true',
            dest='batch',
            help='Export all batch',
        )
        parser.add_argument(
            '--repair',
            action='store_true',
            dest='repair',
            help='Export repair in progress',
        )
        parser.add_argument(
            '--cal_ecu',
            action='store_true',
            dest='cal_ecu',
            help='Export CAL ECU',
        )
        parser.add_argument(
            '--check_out',
            action='store_true',
            dest='check_out',
            help='Export REMAN REFERENCE for Check Out repair',
        )
        parser.add_argument(
            '--scan_in_out',
            action='store_true',
            dest='scan_in_out',
            help='Export REMAN REFERENCE for Scan IN/OUT',
        )

    def handle(self, *args, **options):
        if options['batch']:
            self.stdout.write("[BATCH] Waiting...")
            last_6_months = timezone.datetime.today() + relativedelta(months=-6)
            filename = conf.BATCH_EXPORT_FILE

            header = [
                'Numero de lot', 'Quantite', 'Ref_REMAN', 'Type_ECU', 'HW_Reference', 'PF_Code', 'Fabriquant',
                'Date_de_Debut', 'Date_de_fin', 'Actif', 'Client', 'Ajoute par', 'Ajoute le'
            ]
            # Batch for PSA
            psa_batch = Batch.objects.filter(end_date__gte=last_6_months).order_by('-end_date')
            values_list = list(psa_batch.values_list(
                'batch_number', 'quantity', 'ecu_ref_base__reman_reference', 'ecu_ref_base__ecu_type__technical_data',
                'ecu_ref_base__ecu_type__hw_reference', 'ecu_ref_base__pf_code', 'ecu_ref_base__ecu_type__supplier_oe',
                'start_date', 'end_date', 'active', 'customer', 'created_by__username', 'created_at'
            ).distinct())
            for path in ROOT_PATHS:
                ExportExcel(values_list=values_list, filename=filename, header=header).file(path)
                self.stdout.write(
                    self.style.SUCCESS(
                        "[BATCH] Export completed: NB_BATCH = {} | FILE = {}".format(
                            psa_batch.count(), os.path.join(path, filename)
                        )
                    )
                )
        if options['repair']:
            self.stdout.write("[REPAIR] Waiting...")

            filename = conf.REPAIR_EXPORT_FILE
            header = ['Numero_Identification', 'Code_Barre', 'Status', 'Controle_Qualite']
            repairs = Repair.objects.exclude(status="Rebut").filter(checkout=False).order_by('identify_number')
            values_list = repairs.values_list('identify_number', 'barcode', 'status', 'quality_control').distinct()
            # values_list = self._repair_list_generate(values_list)
            for path in ROOT_PATHS:
                ExportExcel(values_list=values_list, filename=filename, header=header).file(path, False)
                self.stdout.write(
                    self.style.SUCCESS(
                        "[REPAIR] Export completed: NB_REPAIR = {} | FILE = {}".format(
                            repairs.count(), os.path.join(path, filename)
                        )
                    )
                )
        if options['cal_ecu']:
            self.stdout.write("[ECU_CAL] Waiting...")

            log_file = LogFile(CSD_ROOT)
            file_name = "liste_CAL_PSA.txt"
            nb_cal = log_file.export_cal_xelon(file_name)
            self.stdout.write(
                self.style.SUCCESS("[ECU_CAL] Export completed: NB_CAL = {} | FILE = {}".format(nb_cal, file_name))
            )
        if options['check_out']:
            self.stdout.write("[CHECK_OUT] Waiting...")

            filename = conf.CHECKOUT_EXPORT_FILE
            header = [
                'REMAN_REFERENCE', 'HW_REFERENCE', 'TYPE_ECU', 'SUPPLIER', 'PSA_BARCODE', 'REF_CAL_OUT', 'REF_PSA_OUT',
                'OPEN_DIAG', 'REF_MAT', 'REF_COMP', 'CAL_KTAG', 'STATUS'
            ]
            queryset = EcuRefBase.objects.exclude(ref_cal_out__exact='').order_by('reman_reference')
            values_list = queryset.values_list(
                'reman_reference', 'ecu_type__hw_reference', 'ecu_type__technical_data', 'ecu_type__supplier_oe',
                'ecu_type__ecumodel__barcode', 'ref_cal_out', 'ref_psa_out', 'open_diag', 'ref_mat', 'ref_comp',
                'cal_ktag', 'status'
            ).distinct()
            for path in ROOT_PATHS:
                ExportExcel(
                    values_list=values_list, filename=filename, header=header).file(path, False)
                self.stdout.write(
                    self.style.SUCCESS(
                        "[CHECK_OUT] Export completed: NB_REMAN = {} | FILE = {}".format(
                            queryset.count(), os.path.join(path, filename)
                        )
                    )
                )

        if options['scan_in_out']:
            self.stdout.write("[SCAN_IN_OUT] Waiting...")
            filename = conf.SCAN_IN_OUT_EXPORT_FILE
            header = [
                'Reference OE', 'REFERENCE REMAN', 'Module Moteur', 'Réf HW', 'FNR', 'CODE BARRE PSA', 'REF FNR',
                'REF CAL OUT', 'REF à créer ', 'REF_PSA_OUT', 'REQ_DIAG', 'OPENDIAG', 'REQ_REF', 'REF_MAT', 'REF_COMP',
                'REQ_CAL', 'CAL_KTAG', 'REQ_STATUS', 'STATUS', 'TEST_CLEAR_MEMORY', 'CLE_APPLI'
            ]
            queryset = EcuRefBase.objects.exclude(test_clear_memory__exact='').order_by('reman_reference')
            values_list = (
                'ecu_type__ecumodel__oe_raw_reference', 'reman_reference', 'ecu_type__technical_data',
                'ecu_type__hw_reference', 'ecu_type__supplier_oe', 'ecu_type__ecumodel__barcode',
                'ecu_type__ecumodel__former_oe_reference', 'ref_cal_out', 'ecu_type__spare_part__code_produit',
                'ref_psa_out', 'req_diag', 'open_diag', 'req_ref', 'ref_mat', 'ref_comp', 'req_cal', 'cal_ktag',
                'req_status', 'status', 'test_clear_memory', 'cle_appli'
            )
            values_list = queryset.values_list(*values_list).distinct()
            values_list = [self._replace_value(val) for val in values_list]
            for path in ROOT_PATHS:
                ExportExcel(
                    values_list=values_list, filename=filename, header=header, novalue="").file(path, False)
                self.stdout.write(
                    self.style.SUCCESS(
                        "[SCAN_IN_OUT] Export completed: NB_REF = {} | FILE = {}".format(
                            queryset.count(), os.path.join(path, filename)
                        )
                    )
                )

    @staticmethod
    def _repair_list_generate(values_list):
        values_list = list(values_list)
        batchs = Batch.objects.filter(active=True, number__gte=900)
        for batch in batchs:
            number = 0
            for ecu in batch.ecu_ref_base.ecu_type.ecumodel_set.all():
                number += 1
                values_list.append((f"{batch.batch_number[:-3]}{number:03d}", ecu.psa_barcode, "Réparé", True))
        return values_list

    @staticmethod
    def _replace_value(tup):
        data = list(tup)
        for index in [0, 6]:
            if data[index] == "":
                data[index] = "#"
        return tuple(data)
