from django.db.models.functions import Cast, TruncSecond
from django.db.models import DateTimeField, CharField
from django.http import Http404

from squalaetp.models import Xelon
from psa.models import Corvet
from reman.models import Batch, Repair, EcuModel
from utils.file.export import ExportExcel


"""
##################################

Export CORVET data to excel format

##################################
"""


def extract_ecu(vin_list=None):
    filename = 'ecu'
    header = [
        'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE', '14A_CMM_HARD',
        '34A_CMM_SOFT_LIVRE', '94A_CMM_SOFT', '44A_CMM_FOURN.NO.SERIE', '54A_CMM_FOURN.DATE.FAB', '64A_CMM_FOURN.CODE',
        '84A_CMM_DOTE', 'P4A_CMM_EOBD'
    ]
    corvets = Corvet.objects.filter(vin__in=vin_list)

    values_list = (
        'xelon__numero_de_dossier', 'vin', 'xelon__modele_produit', 'xelon__modele_vehicule',
        'donnee_date_debut_garantie', 'electronique_14a', 'electronique_34a', 'electronique_94a', 'electronique_44a',
        'electronique_54a', 'electronique_64a', 'electronique_84a', 'electronique_p4a'
    )

    return ExportExcel(queryset=corvets, filename=filename, header=header, values_list=values_list).http_response()


def extract_corvet(product='corvet', excel_type='csv'):
    filename = product
    header = queryset = values_list = None
    if product == "ecu":
        header = [
            'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE', '14A_CMM_HARD',
            '34A_CMM_SOFT_LIVRE', '94A_CMM_SOFT', '44A_CMM_FOURN.NO.SERIE', '54A_CMM_FOURN.DATE.FAB',
            '64A_CMM_FOURN.CODE',
            '84A_CMM_DOTE', 'P4A_CMM_EOBD'
        ]
        queryset = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_14a__exact='').annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = (
            'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_debut_garantie',
            'corvet__electronique_14a', 'corvet__electronique_34a', 'corvet__electronique_94a',
            'corvet__electronique_44a',
            'corvet__electronique_54a', 'corvet__electronique_64a', 'corvet__electronique_84a',
            'corvet__electronique_p4a'
        )
    elif product == "bsi":
        header = [
            'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE', '14B_BSI_HARD',
            '94B_BSI_SOFT', '44B_BSI_FOURN.NO.SERIE', '54B_BSI_FOURN.DATE.FAB', '64B_BSI_FOURN.CODE', '84B_BSI_DOTE'
        ]

        queryset = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_14b__exact='').annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = (
            'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_debut_garantie',
            'corvet__electronique_14b', 'corvet__electronique_94b', 'corvet__electronique_44b',
            'corvet__electronique_54b',
            'corvet__electronique_64b', 'corvet__electronique_84b',
        )
    elif product == "com200x":
        header = [
            'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE', '16P_HDC_HARD',
            '46P_HDC_FOURN.NO.SERIE', '56P_HDC_FOURN.DATE.FAB', '66P_HDC_FOURN.CODE'
        ]

        queryset = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_16p__exact='').annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = (
            'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_debut_garantie',
            'corvet__electronique_16p', 'corvet__electronique_46p', 'corvet__electronique_56p',
            'corvet__electronique_66p'
        )
    elif product == "bsm":
        header = [
            'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE', '16B_BSM_HARD',
            '46B_BSM_FOURN.NO.SERIE', '56B_BSM_FOURN.DATE.FAB', '66B_BSM_FOURN.CODE', '86B_BSM_DOTE', '96B_BSM_SOFT'
        ]

        queryset = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_16p__exact='').annotate(
            date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
        )
        values_list = (
            'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_debut_garantie',
            'corvet__electronique_16b', 'corvet__electronique_46b', 'corvet__electronique_56b',
            'corvet__electronique_66b',
            'corvet__electronique_86b', 'corvet__electronique_96b'
        )
    elif product == 'corvet':
        header = [
            'V.I.N.', 'DATE_DEBUT_GARANTIE', 'DATE_ENTREE_MONTAGE', 'LIGNE_DE_PRODUIT', 'MARQUE_COMMERCIALE',
            'SILHOUETTE', 'GENRE_DE_PRODUIT', 'DDO', 'DGM', 'DHB', 'DHG', 'DJQ', 'DJY', 'DKX', 'DLX', 'DOI', 'DQM',
            'DQS', 'DRC', 'DRT', 'DTI', 'DUN', 'DWL', 'DWT', 'DXJ', 'DYB', 'DYM', 'DYR', 'DZV', 'GG8', '14F', '14J',
            '14K', '14L', '14R', '14X', '19Z', '44F', '44L', '44X', '54F', '54K', '54L', '84F', '84L', '84X', '94F',
            '94L', '94X', 'DAT', 'DCX', '19H', '49H', '64F', '64X', '69H', '89H', '99H', '14A', '34A', '44A', '54A',
            '64A', '84A', '94A', 'P4A', 'MOTEUR', 'TRANSMISSION', '10', '14B', '20', '44B', '54B', '64B', '84B', '94B',
            '16P', '46P', '56P', '66P', '16B', '46B', '56B', '66B', '86B', '96B'
        ]
        queryset = Corvet.objects.all()
        values_list = None
    if queryset:
        return ExportExcel(queryset, filename, header, values_list, excel_type).http_response()
    else:
        raise Http404("No data matches")


"""
##################################

Export REMAN data to excel format

##################################
"""


def extract_reman(model, excel_type='csv'):
    filename = model
    header = queryset = values_list = None
    if model == "batch":
        header = [
            'Numero de lot', 'Quantite', 'Ref_REMAN', 'Type_ECU', 'HW_Reference', 'Fabriquant', 'Date_de_Debut',
            'Date_de_fin', 'Actif', 'Ajoute par', 'Ajoute le'
        ]
        queryset = Batch.objects.all().order_by('batch_number')
        values_list = (
            'batch_number', 'quantity', 'ecu_ref_base__reman_reference', 'ecu_ref_base__ecu_type__technical_data',
            'ecu_ref_base__ecu_type__hw_reference', 'ecu_ref_base__ecu_type__supplier_oe', 'start_date', 'end_date',
            'active', 'created_by__username', 'created_at'
        )
    elif model == "repair_reman":
        header = [
            'Numero_identification', 'Numero_lot', 'Ref_REMAN', 'Type_ECU', 'Fabriquant', 'HW_Reference',
            'Code_barre_PSA', 'Code_defaut', 'Libelle_defaut', 'Commentaires_action', 'status', 'Controle_qualite',
            'Date_de_cloture', 'Modifie_par', 'Modifie_le', 'Cree par', 'Cree_le'
        ]
        queryset = Repair.objects.all().order_by('identify_number')
        values_list = (
            'identify_number', 'batch__batch_number', 'batch__ecu_ref_base__reman_reference',
            'batch__ecu_ref_base__ecu_type__technical_data', 'batch__ecu_ref_base__ecu_type__supplier_oe',
            'batch__ecu_ref_base__ecu_type__hw_reference', 'psa_barcode', 'default__code', 'default__description',
            'comment', 'status', 'quality_control', 'closing_date', 'modified_by__username', 'modified_at',
            'created_at', 'created_by__username',
        )
    elif model == "base_ref_reman":
        header = [
            'Reference OE', 'REFERENCE REMAN', 'Module Moteur', 'Réf HW', 'FNR', 'CODE BARRE PSA', 'REF FNR',
            'REF CAL OUT', 'REF à créer ', 'REF_PSA_OUT', 'OPENDIAG', 'REF_MAT', 'REF_COMP', 'CAL_KTAG', 'STATUT'
        ]
        queryset = EcuModel.objects.all().order_by('ecu_type__ecu_ref_base__reman_reference')
        values_list = (
            'oe_raw_reference', 'ecu_type__ecu_ref_base__reman_reference', 'ecu_type__technical_data',
            'ecu_type__hw_reference', 'ecu_type__supplier_oe', 'psa_barcode', 'former_oe_reference',
            'ecu_type__ecu_ref_base__ref_cal_out', 'ecu_type__spare_part__code_produit',
            'ecu_type__ecu_ref_base__ref_psa_out', 'ecu_type__ecu_ref_base__open_diag',
            'ecu_type__ecu_ref_base__ref_mat', 'ecu_type__ecu_ref_base__ref_comp', 'ecu_type__ecu_ref_base__cal_ktag',
            'ecu_type__ecu_ref_base__status'

        )

    if queryset:
        return ExportExcel(queryset, filename, header, values_list, excel_type).http_response()
    else:
        raise Http404("No data matches")
