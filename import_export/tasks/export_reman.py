import os.path

from openpyxl import Workbook

from django.db.models import Q, Count

from utils.file.export_task import ExportExcelTask
from reman.models import Batch, Repair, EcuRefBase

REMAN_DICT = {
    'batch': [
        ('Numero de lot', 'batch_number'), ('Quantite', 'quantity'), ('Ref_REMAN', 'ecu_ref_base__reman_reference'),
        ('Client', 'customer'), ('Réparés', 'repaired'), ('Rebuts', 'rebutted'), ('Emballés', 'packed'),
        ('Total', 'total'), ('Date_de_Debut', 'start_date'), ('Date_de_fin', 'end_date'),
        ('Type_ECU', 'ecu_ref_base__ecu_type__technical_data'),
        ('HW_Reference', 'ecu_ref_base__ecu_type__hw_reference'), ('Fabriquant', 'ecu_ref_base__ecu_type__supplier_oe'),
        ('Actif', 'active')
    ],
    'repair': [
        ('Numero_identification', 'identify_number'), ('Numero_lot', 'batch__batch_number'),
        ('Ref_REMAN', 'batch__ecu_ref_base__reman_reference'),
        ('Type_ECU', 'batch__ecu_ref_base__ecu_type__technical_data'),
        ('Fabriquant', 'batch__ecu_ref_base__ecu_type__supplier_oe'),
        ('HW_Reference', 'batch__ecu_ref_base__ecu_type__hw_reference'),
        ('Code_barre', 'barcode'), ('Nouveau_code_barre', 'new_barcode'), ('Code_defaut', 'default__code'),
        ('Libelle_defaut', 'default__description'), ('Commentaires_action', 'comment'), ('status', 'status'),
        ('Controle_qualite', 'quality_control'), ('Date_de_cloture', 'closing_date')
    ],
    'base_ref': [
        ('Reference OE', 'ecu_type__ecumodel__oe_raw_reference'), ('REFERENCE REMAN', 'reman_reference'),
        ('Module Moteur', 'ecu_type__technical_data'), ('Réf HW', 'ecu_type__hw_reference'),
        ('FNR', 'ecu_type__supplier_oe'), ('CODE BARRE PSA', 'ecu_type__ecumodel__barcode'),
        ('REF FNR', 'ecu_type__ecumodel__former_oe_reference'), ('REF CAL OUT', 'ref_cal_out'),
        ('REF à créer ', 'ecu_type__spare_part__code_produit'), ('REF_PSA_OUT', 'ref_psa_out'),
        ('REQ_DIAG', 'req_diag'), ('OPENDIAG', 'open_diag'), ('REQ_REF', 'req_ref'), ('REF_MAT', 'ref_mat'),
        ('REF_COMP', 'ref_comp'), ('REQ_CAL', 'req_cal'), ('CAL_KTAG', 'cal_ktag'), ('REQ_STATUS', 'req_status'),
        ('STATUS', 'status'), ('TEST_CLEAR_MEMORY', 'test_clear_memory'), ('CLE_APPLI', 'cle_appli')
    ],
    'created': [
        ('Cree par', 'created_by__username'), ('Cree_le', 'created_at'),
    ],
    'updated': [
        ('Modifie_par', 'modified_by__username'), ('Modifie_le', 'modified_at')
    ],
    'remanufacturing': [
        ('FACE PLATE', 'face_plate'), ('FAN', 'fan'), ('REAR BOLT', 'locating_pin'), ('METAL CASE', 'metal_case')
    ]
}


class ExportRemanIntoExcelTask(ExportExcelTask):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        path = self.copy_and_get_copied_path()
        excel_type = kwargs.pop('excel_type', 'xlsx')
        model = kwargs.pop('table', 'batch')
        filename = f"{model}_{self.date.strftime('%y-%m-%d_%H-%M')}"
        if model == "base_ref_reman":
            values_list = self.extract_ecurefbase(*args, **kwargs)
        elif model == "repair_reman":
            values_list = self.extract_repair(*args, **kwargs)
        else:
            values_list = self.extract_batch(*args, **kwargs)
        destination_path = os.path.join(path, f"{filename}.{excel_type}")
        workbook = Workbook()
        workbook = self.create_workbook(workbook, self.header, values_list)
        workbook.save(filename=destination_path)
        return {
            "detail": "Successfully export REMAN",
            "data": {
                "outfile": destination_path
            }
        }

    def extract_batch(self, *args, **kwargs):
        """
        Export Batch data to excel format
        """
        data_list = REMAN_DICT['batch'] + REMAN_DICT['created']
        repaired = Count('repairs', filter=Q(repairs__status="Réparé"))
        rebutted = Count('repairs', filter=Q(repairs__status="Rebut"))
        packed = Count('repairs', filter=Q(repairs__checkout=True))
        queryset = Batch.objects.all().order_by('batch_number')
        queryset = queryset.annotate(repaired=repaired, packed=packed, rebutted=rebutted, total=Count('repairs'))
        self.header, self.fields = self.get_header_fields(data_list)
        return queryset.values_list(*self.fields).distinct()

    def extract_ecurefbase(self, *args, **kwargs):
        """
        Export EcuRefBase data to excel format
        """
        data_list = REMAN_DICT['base_ref']
        queryset = EcuRefBase.objects.exclude(test_clear_memory__exact='').order_by('reman_reference')
        self.header, self.fields = self.get_header_fields(data_list)
        return queryset.values_list(*self.fields).distinct()

    def extract_repair(self, *args, **kwargs):
        """
        Export Repair data to excel format
        """
        data_list = REMAN_DICT['repair'] + REMAN_DICT['remanufacturing'] + REMAN_DICT['created']
        data_list += REMAN_DICT['updated']
        queryset = Repair.objects.all().order_by('identify_number')
        if kwargs.get('customer', None):
            queryset = queryset.filter(batch__customer=kwargs.get('customer'))
        if kwargs.get('batch_number', None):
            queryset = queryset.filter(batch__batch_number=kwargs.get('batch_number'))
        self.header, self.fields = self.get_header_fields(data_list)
        values_list = queryset.values_list(*self.fields).distinct()
        if "repair_parts" in kwargs.get('columns', []):
            self.textCols = [len(data_list) + 1, len(data_list) + 2]
            values_list = self._add_parts(values_list)
        return values_list

    def _add_parts(self, values_list):
        self.header.extend(["Code_produit (PART)", "Quantité (PART)"])
        new_values_list = []
        for values in values_list:
            values = list(values)
            try:
                product_code, quantity = "", ""
                for part in Repair.objects.get(identify_number=values[0]).parts.all():
                    product_code += f"{part.product_code} \r\n"
                    quantity += f"{part.quantity} \r\n"
                values.extend([product_code.strip(), quantity.strip()])
            except Repair.DoesNotExist:
                pass
            finally:
                new_values_list.append(values)
        return new_values_list
