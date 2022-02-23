from django.db.models import Q, Count

from . import get_header_fields

from reman.models import Batch, Repair, EcuRefBase


REMAN_DICT = {
    'batch': [
        ('Numero de lot', 'batch_number'), ('Quantite', 'quantity'), ('Ref_REMAN', 'ecu_ref_base__reman_reference'),
        ('Client', 'customer'), ('Réparés', 'repaired'), ('Rebuts', 'rebutted'), ('Emballés', 'packed'),
        ('Total', 'total'), ('Date_de_Debut', 'start_date'), ('Date_de_fin', 'end_date'),
        ('Type_ECU', 'ecu_ref_base__ecu_type__technical_data'),
        ('HW_Reference', 'ecu_ref_base__ecu_type__hw_reference'), ('Fabriquant', 'ecu_ref_base__ecu_type__supplier_oe'),
        ('Actif', 'active'), ('Ajoute par', 'created_by__username'), ('Ajoute le', 'created_at')
    ],
    'repair': [
        ('Numero_identification', 'identify_number'), ('Numero_lot', 'batch__batch_number'),
        ('Ref_REMAN', 'batch__ecu_ref_base__reman_reference'),
        ('Type_ECU', 'batch__ecu_ref_base__ecu_type__technical_data'),
        ('Fabriquant', 'batch__ecu_ref_base__ecu_type__supplier_oe'),
        ('HW_Reference', 'batch__ecu_ref_base__ecu_type__hw_reference'),
        ('Code_barre', 'barcode'), ('Nouveau_code_barre', 'new_barcode'), ('Code_defaut', 'default__code'),
        ('Libelle_defaut', 'default__description'), ('Commentaires_action', 'comment'), ('status', 'status'),
        ('Controle_qualite', 'quality_control'), ('Date_de_cloture', 'closing_date'),
    ],
    'repair_end': [
        ('Cree par', 'created_by__username'), ('Cree_le', 'created_at'), ('Modifie_par', 'modified_by__username'),
        ('Modifie_le', 'modified_at')
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
    'remanufacturing': [
        ('FACE PLATE', 'face_plate'), ('FAN', 'fan'), ('REAR BOLT', 'locating_pin'), ('METAL CASE', 'metal_case')
    ]
}


def add_parts(header, values_list):
    header = list(header)
    header.extend(["Code_produit (PART)", "Quantité (PART)"])
    new_values_list = []
    for values in values_list:
        values = list(values)
        try:
            product_code, quantity = "", ""
            for part in Repair.objects.get(identify_number=values[0]).parts.all():
                product_code += f"{part.product_code}\n"
                quantity += f"{part.quantity}\n"
            values.extend([product_code.strip(), quantity.strip()])
        except Repair.DoesNotExist:
            pass
        finally:
            new_values_list.append(values)
    return header, new_values_list


def extract_reman(*args, **kwargs):
    """
    Export REMAN data to excel format
    """
    queryset = data_list = None
    model = kwargs.get("table", "batch")
    if model == "batch":
        data_list = REMAN_DICT.get('batch')
        repaired = Count('repairs', filter=Q(repairs__status="Réparé"))
        rebutted = Count('repairs', filter=Q(repairs__status="Rebut"))
        packed = Count('repairs', filter=Q(repairs__checkout=True))
        queryset = Batch.objects.all().order_by('batch_number')
        queryset = queryset.annotate(repaired=repaired, packed=packed, rebutted=rebutted, total=Count('repairs'))
    elif model == "repair_reman":
        data_list = REMAN_DICT.get('repair')
        for col in kwargs.get('columns', []):
            data_list += REMAN_DICT.get(col, [])
        data_list += REMAN_DICT.get('repair_end')
        queryset = Repair.objects.all().order_by('identify_number')
        if kwargs.get('customer', None):
            queryset = queryset.filter(batch__customer=kwargs.get('customer'))
        if kwargs.get('batch_number', None):
            queryset = queryset.filter(batch__batch_number=kwargs.get('batch_number'))
    elif model == "base_ref_reman":
        data_list = REMAN_DICT.get('base_ref')
        queryset = EcuRefBase.objects.exclude(test_clear_memory__exact='').order_by('reman_reference')
    header, values_list = get_header_fields(data_list)
    fields = values_list
    values_list = queryset.values_list(*values_list).distinct()
    if model == "repair_reman" and "repair_parts" in kwargs.get('columns'):
        header, values_list = add_parts(header, values_list)
    return header, fields, values_list
