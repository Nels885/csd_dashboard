from django.db.models import Q, Count

from . import get_header_fields

from reman.models import Batch, Repair, EcuRefBase


REMAN_DICT = {
    'remanufacturing': [
        ('FACE PLATE', 'face_plate'), ('FAN', 'fan'), ('REAR BOLT', 'locating_pin'), ('METAL CASE', 'metal_case')
    ]
}


def extract_reman(*args, **kwargs):
    """
    Export REMAN data to excel format
    """
    header = queryset = values_list = None
    model = kwargs.get("table", "batch")
    if model == "batch":
        header = [
            'Numero de lot', 'Quantite', 'Ref_REMAN', 'Client', 'Réparés', 'Rebuts', 'Emballés', 'Total',
            'Date_de_Debut', 'Date_de_fin', 'Type_ECU', 'HW_Reference', 'Fabriquant', 'Actif', 'Ajoute par', 'Ajoute le'
        ]
        repaired = Count('repairs', filter=Q(repairs__status="Réparé"))
        rebutted = Count('repairs', filter=Q(repairs__status="Rebut"))
        packed = Count('repairs', filter=Q(repairs__checkout=True))
        queryset = Batch.objects.all().order_by('batch_number')
        queryset = queryset.annotate(repaired=repaired, packed=packed, rebutted=rebutted, total=Count('repairs'))
        values_list = (
            'batch_number', 'quantity', 'ecu_ref_base__reman_reference', 'customer', 'repaired', 'rebutted', 'packed',
            'total', 'start_date', 'end_date', 'ecu_ref_base__ecu_type__technical_data',
            'ecu_ref_base__ecu_type__hw_reference', 'ecu_ref_base__ecu_type__supplier_oe', 'active',
            'created_by__username', 'created_at'
        )
    elif model == "repair_reman":
        queryset = Repair.objects.all().order_by('identify_number')
        if kwargs.get('customer', None):
            queryset = queryset.filter(batch__customer=kwargs.get('customer'))
        if kwargs.get('batch_number', None):
            queryset = queryset.filter(batch__batch_number=kwargs.get('batch_number'))
        header = [
            'Numero_identification', 'Numero_lot', 'Ref_REMAN', 'Type_ECU', 'Fabriquant', 'HW_Reference',
            'Code_barre', 'Nouveau_code_barre' 'Code_defaut', 'Libelle_defaut', 'Commentaires_action', 'status',
            'Controle_qualite', 'Date_de_cloture', 'Modifie_par', 'Modifie_le', 'Cree par', 'Cree_le'
        ]
        values_list = (
            'identify_number', 'batch__batch_number', 'batch__ecu_ref_base__reman_reference',
            'batch__ecu_ref_base__ecu_type__technical_data', 'batch__ecu_ref_base__ecu_type__supplier_oe',
            'batch__ecu_ref_base__ecu_type__hw_reference', 'barcode', 'new_barcode', 'default__code',
            'default__description', 'comment', 'status', 'quality_control', 'closing_date', 'modified_by__username',
            'modified_at', 'created_at', 'created_by__username',
        )
    elif model == "base_ref_reman":
        header = [
            'Reference OE', 'REFERENCE REMAN', 'Module Moteur', 'Réf HW', 'FNR', 'CODE BARRE PSA', 'REF FNR',
            'REF CAL OUT', 'REF à créer ', 'REF_PSA_OUT', 'REQ_DIAG', 'OPENDIAG', 'REQ_REF', 'REF_MAT', 'REF_COMP',
            'REQ_CAL', 'CAL_KTAG', 'REQ_STATUS', 'STATUS', 'TEST_CLEAR_MEMORY', 'CLE_APPLI'
        ]
        queryset = EcuRefBase.objects.exclude(test_clear_memory__exact='').order_by('reman_reference')
        values_list = (
            'ecu_type__ecumodel__oe_raw_reference', 'reman_reference', 'ecu_type__technical_data',
            'ecu_type__hw_reference', 'ecu_type__supplier_oe', 'ecu_type__ecumodel__psa_barcode',
            'ecu_type__ecumodel__former_oe_reference', 'ref_cal_out', 'ecu_type__spare_part__code_produit',
            'ref_psa_out', 'req_diag', 'open_diag', 'req_ref', 'ref_mat', 'ref_comp', 'req_cal', 'cal_ktag',
            'req_status', 'status', 'test_clear_memory', 'cle_appli'
        )
    fields = values_list
    values_list = queryset.values_list(*values_list).distinct()
    return header, fields, values_list
