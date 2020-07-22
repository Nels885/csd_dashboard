from django.core.management.base import BaseCommand

from reman.models import Batch

from utils.file.export import ExportExcel, os
from utils.conf import CSD_ROOT


class Command(BaseCommand):
    help = 'Export CSV file for Batch REMAN'

    def handle(self, *args, **options):
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
            self.style.SUCCESS("export BATCH completed: NB_BATCH = {} | FILE = {}.csv".format(batch.count(), filename))
        )
