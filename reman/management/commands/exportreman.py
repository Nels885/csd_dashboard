from django.core.management.base import BaseCommand

from reman.models import Batch, Repair, EcuRefBase

from utils.file.export import ExportExcel, os
from utils.conf import CSD_ROOT, conf
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

    def handle(self, *args, **options):
        if options['batch']:
            self.stdout.write("[BATCH] Waiting...")

            filename = conf.BATCH_EXPORT_FILE
            path = os.path.join(CSD_ROOT, conf.EXPORT_PATH)
            header = [
                'Numero de lot', 'Quantite', 'Ref_REMAN', 'Type_ECU', 'HW_Reference', 'Fabriquant', 'Date_de_Debut',
                'Date_de_fin', 'Actif', 'Ajoute par', 'Ajoute le'
            ]
            batch = Batch.objects.all().order_by('batch_number')
            values_list = (
                'batch_number', 'quantity', 'ecu_ref_base__reman_reference', 'ecu_ref_base__ecu_type__technical_data',
                'ecu_ref_base__ecu_type__hw_reference', 'ecu_ref_base__ecu_type__supplier_oe', 'start_date', 'end_date',
                'active', 'created_by__username', 'created_at'
            )
            ExportExcel(queryset=batch, filename=filename, header=header, values_list=values_list).file(path)
            self.stdout.write(
                self.style.SUCCESS(
                    "[BATCH] Export completed: NB_BATCH = {} | FILE = {}.csv".format(batch.count(), filename)
                )
            )
        elif options['repair']:
            self.stdout.write("[REPAIR] Waiting...")

            filename = conf.REPAIR_EXPORT_FILE
            path = os.path.join(CSD_ROOT, conf.EXPORT_PATH)
            header = ['Numero_Identification', 'Code_Barre_PSA', 'Status', 'Controle_Qualite']
            repairs = Repair.objects.exclude(status="Rebut").filter(checkout=False).order_by('identify_number')
            values_list = ('identify_number', 'psa_barcode', 'status', 'quality_control')
            ExportExcel(queryset=repairs, filename=filename, header=header, values_list=values_list).file(path, False)
            self.stdout.write(
                self.style.SUCCESS(
                    "[REPAIR] Export completed: NB_REPAIR = {} | FILE = {}.csv".format(repairs.count(), filename)
                )
            )
        elif options['cal_ecu']:
            self.stdout.write("[ECU_CAL] Waiting...")

            log_file = LogFile(CSD_ROOT)
            file_name = "liste_CAL_PSA.txt"
            nb_cal = log_file.export_cal_xelon(file_name)
            self.stdout.write(
                self.style.SUCCESS("[ECU_CAL] Export completed: NB_CAL = {} | FILE = {}".format(nb_cal, file_name))
            )
        elif options['check_out']:
            self.stdout.write("[CHECK_OUT] Waiting...")

            filename = conf.CHECKOUT_EXPORT_FILE
            path = os.path.join(CSD_ROOT, conf.EXPORT_PATH)
            header = [
                'REMAN_REFERENCE', 'HW_REFERENCE', 'TYPE_ECU', 'SUPPLIER', 'PSA_BARCODE', 'REF_CAL_OUT', 'REF_PSA_OUT',
                'OPEN_DIAG', 'REF_MAT', 'REF_COMP', 'CAL_KTAG', 'STATUS'
            ]
            ecu = EcuRefBase.objects.exclude(ref_cal_out__exact='').order_by('reman_reference')
            values_list = (
                'reman_reference', 'ecu_type__hw_reference', 'ecu_type__technical_data', 'ecu_type__supplier_oe',
                'ecu_type__ecumodel__psa_barcode', 'ref_cal_out', 'ref_psa_out', 'open_diag', 'ref_mat', 'ref_comp',
                'cal_ktag', 'status'
            )
            ExportExcel(queryset=ecu, filename=filename, header=header, values_list=values_list).file(path, False)
            self.stdout.write(
                self.style.SUCCESS(
                    "[CHECK_OUT] Export completed: NB_REMAN = {} | FILE = {}.csv".format(ecu.count(), filename)
                )
            )
