from django.core.management.base import BaseCommand

from reman.models import Batch, Repair

from utils.file.export import ExportExcel, os
from utils.conf import CSD_ROOT
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

    def handle(self, *args, **options):
        if options['batch']:
            self.stdout.write("[BATCH] Waiting...")

            filename = "lots_reman"
            path = os.path.join(CSD_ROOT, "EXTS")
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

            filename = "repairs_reman"
            path = os.path.join(CSD_ROOT, "EXTS")
            header = ['Numero_Identification', 'Code_Barre_PSA', 'Status', 'Controle_Qualite']
            batch = Repair.objects.filter(status="Réparé", quality_control=True).order_by('identify_number')
            values_list = ('identify_number', 'psa_barcode', 'status', 'quality_control')
            ExportExcel(queryset=batch, filename=filename, header=header, values_list=values_list).file(path, False)
            self.stdout.write(
                self.style.SUCCESS(
                    "[REPAIR] Export completed: NB_REPAIR = {} | FILE = {}.csv".format(batch.count(), filename)
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
