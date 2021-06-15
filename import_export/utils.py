from django.db.models.functions import Cast, TruncSecond, Concat, ExtractDay
from django.db.models import DateTimeField, CharField, Q, Count, Value, F

from squalaetp.models import Xelon
from psa.models import Corvet
from reman.models import Batch, Repair, EcuType
from tools.models import Suptech, BgaTime

XELON_LIST = [
    ('Dossier (XELON)', 'numero_de_dossier'), ('V.I.N. (XELON)', 'vin'), ('Produit (XELON)', 'modele_produit'),
    ('Vehicule (XELON)', 'modele_vehicule'), ('Date Retour (XELON)', 'date_retour')
]

BTEL_LIST = [
    ('Modele reel', 'corvet__prods__btel__name'), ('Réf. Setplate', 'corvet__prods__btel__label_ref'),
    ('Niv.', 'corvet__prods__btel__level'), ('HW variant', 'corvet__prods__btel__extra'),
    ('DATE_DEBUT_GARANTIE', 'date_debut_garantie'), ('LIGNE_DE_PRODUIT', 'corvet__donnee_ligne_de_produit'),
    ('SILHOUETTE', 'corvet__donnee_silhouette'), ('GENRE_DE_PRODUIT', 'corvet__donnee_genre_de_produit'),
    ('DHB_HAUT PARLEUR', 'corvet__attribut_dhb'), ('DUN_AMPLI EQUALISEUR', 'corvet__attribut_dun'),
    ('DYR_BTA', 'corvet__attribut_dyr'), ('14X_BTEL_HARD', 'corvet__electronique_14x'),
    ('44X_BTEL_FOURN.NO.SERIE', 'corvet__electronique_44x'), ('64X_BTEL_FOURN.CODE', 'corvet__electronique_64x'),
    ('84X_BTEL_DOTE', 'corvet__electronique_84x'), ('94X_BTEL_SOFT', 'corvet__electronique_94x')
]

CMM_LIST = [
    ('Modele reel', 'corvet__prods__cmm__name'),
    ('DATE_DEBUT_GARANTIE', 'date_debut_garantie'), ('LIGNE_DE_PRODUIT', 'corvet__donnee_ligne_de_produit'),
    ('SILHOUETTE', 'corvet__donnee_silhouette'), ('GENRE_DE_PRODUIT', 'corvet__donnee_genre_de_produit'),
    ('14A_CMM_HARD', 'corvet__electronique_14a'), ('34A_CMM_SOFT_LIVRE', 'corvet__electronique_34a'),
    ('94A_CMM_SOFT', 'corvet__electronique_94a'), ('44A_CMM_FOURN.NO.SERIE', 'corvet__electronique_44b'),
    ('54A_CMM_FOURN.DATE.FAB', 'corvet__electronique_54b'), ('64A_CMM_FOURN.CODE', 'corvet__electronique_64b'),
    ('84A_CMM_DOTE', 'corvet__electronique_84a'), ('P4A_CMM_EOBD', 'corvet__electronique_p4a')
]

BSI_LIST = [
    ('Modele reel', 'corvet__prods__bsi__name'), ('HW', 'corvet__prods__bsi__hw'), ('SW', 'corvet__prods__bsi__sw'),
    ('DATE_DEBUT_GARANTIE', 'date_debut_garantie'), ('LIGNE_DE_PRODUIT', 'corvet__donnee_ligne_de_produit'),
    ('SILHOUETTE', 'corvet__donnee_silhouette'), ('MOTEUR', 'corvet__donnee_moteur'),
    ('CAL MOTEUR', 'corvet__prods__cmm__name'), ('14B_BSI_HARD', 'corvet__electronique_14b'),
    ('94B_BSI_SOFT', 'corvet__electronique_94b'), ('44B_BSI_FOURN.NO.SERIE', 'corvet__electronique_44b'),
    ('54B_BSI_FOURN.DATE.FAB', 'corvet__electronique_54b'), ('64B_BSI_FOURN.CODE', 'corvet__electronique_64b'),
    ('84B_BSI_DOTE', 'corvet__electronique_84b')
]

HDC_LIST = [
    ('DATE_DEBUT_GARANTIE', 'date_debut_garantie'), ('LIGNE_DE_PRODUIT', 'corvet__donnee_ligne_de_produit'),
    ('SILHOUETTE', 'corvet__donnee_silhouette'), ('16P_HDC_HARD', 'corvet__electronique_16p'),
    ('46P_HDC_FOURN.NO.SERIE', 'corvet__electronique_46p'), ('56P_HDC_FOURN.DATE.FAB', 'corvet__electronique_56p'),
    ('66P_HDC_FOURN.CODE', 'corvet__electronique_66p')
]

BSM_LIST = [
    ('DATE_DEBUT_GARANTIE', 'date_debut_garantie'), ('LIGNE_DE_PRODUIT', 'corvet__donnee_ligne_de_produit'),
    ('SILHOUETTE', 'corvet__donnee_silhouette'), ('16B_BSM_HARD', 'corvet__electronique_16b'),
    ('46B_BSM_FOURN.NO.SERIE', 'corvet__electronique_46b'), ('56B_BSM_FOURN.DATE.FAB', 'corvet__electronique_56b'),
    ('66B_BSM_FOURN.CODE', 'corvet__electronique_66b'), ('86B_BSM_DOTE', 'corvet__electronique_86b'),
    ('96B_BSM_SOFT', 'corvet__electronique_96b')
]


def get_header_fields(prod_list):
    header = [value_tuple[0] for value_tuple in XELON_LIST] + [value_tuple[0] for value_tuple in prod_list]
    fields = [value_tuple[1] for value_tuple in XELON_LIST] + [value_tuple[1] for value_tuple in prod_list]
    return header, fields


BTEL_HEADER, BTEL_FIELDS = get_header_fields(BTEL_LIST)
CMM_HEADER, CMM_FIELDS = get_header_fields(CMM_LIST)
BSI_HEADER, BSI_FIELDS = get_header_fields(BSI_LIST)
HDC_HEADER, HDC_FIELDS = get_header_fields(HDC_LIST)
BSM_HEADER, BSM_FIELDS = get_header_fields(BSM_LIST)

"""
##################################

Export CORVET data to excel format

##################################
"""


def extract_ecu(vin_list=None):
    header = [
        'Numero de dossier', 'V.I.N.', 'Modele produit', 'Modele vehicule', 'DATE_DEBUT_GARANTIE', '14A_CMM_HARD',
        '34A_CMM_SOFT_LIVRE', '94A_CMM_SOFT', '44A_CMM_FOURN.NO.SERIE', '54A_CMM_FOURN.DATE.FAB', '64A_CMM_FOURN.CODE',
        '84A_CMM_DOTE', 'P4A_CMM_EOBD'
    ]
    corvets = Corvet.objects.filter(vin__in=vin_list)

    fields = [
        'xelon__numero_de_dossier', 'vin', 'xelon__modele_produit', 'xelon__modele_vehicule',
        'donnee_date_debut_garantie', 'electronique_14a', 'electronique_34a', 'electronique_94a', 'electronique_44a',
        'electronique_54a', 'electronique_64a', 'electronique_84a', 'electronique_p4a'
    ]
    values_list = corvets.values_list(*fields).distinct()
    return header, fields, values_list


def extract_corvet(product='corvet'):
    values_list = ()
    header = queryset = None
    xelons = Xelon.objects.filter(corvet__isnull=False).annotate(
        date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
    )
    if product == "ecu":
        header, values_list = CMM_HEADER, CMM_FIELDS
        queryset = xelons.exclude(corvet__electronique_14a__exact='')
    elif product == "bsi":
        header, values_list = BSI_HEADER, BSI_FIELDS
        queryset = xelons.exclude(corvet__electronique_14b__exact='')
    elif product == "com200x":
        header, values_list = HDC_HEADER, HDC_FIELDS
        queryset = xelons.exclude(corvet__electronique_16p__exact='')
    elif product == "bsm":
        header, values_list = BSM_HEADER, BSM_FIELDS
        queryset = xelons.exclude(corvet__electronique_16p__exact='')
    elif product == "nac":
        header, values_list = BTEL_HEADER, BTEL_FIELDS
        queryset = xelons.filter(modele_produit__startswith="NAC")
    elif product == "rtx":
        header, values_list = BTEL_HEADER, BTEL_FIELDS
        queryset = xelons.filter(modele_produit__startswith="RT")
    elif product == "smeg":
        header, values_list = BTEL_HEADER, BTEL_FIELDS
        queryset = xelons.filter(modele_produit__startswith="SMEG")
    elif product == "rneg":
        header, values_list = BTEL_HEADER, BTEL_FIELDS
        queryset = xelons.filter(modele_produit__startswith="RNEG")
    elif product == "ng4":
        header, values_list = BTEL_HEADER, BTEL_FIELDS
        queryset = xelons.filter(modele_produit__startswith="NG4")
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
        values_list = tuple([field.name for col_nb, field in enumerate(Corvet._meta.fields)
                             if col_nb < len(header)])
    fields = values_list
    values_list = queryset.values_list(*values_list).distinct()
    return header, fields, values_list


"""
##################################

Export REMAN data to excel format

##################################
"""


def extract_reman(model):
    header = queryset = values_list = None
    if model == "batch":
        header = [
            'Numero de lot', 'Quantite', 'Ref_REMAN', 'Réparés', 'Rebuts', 'Emballés', 'Total', 'Date_de_Debut',
            'Date_de_fin', 'Type_ECU', 'HW_Reference', 'Fabriquant',  'Actif', 'Ajoute par', 'Ajoute le'
        ]
        repaired = Count('repairs', filter=Q(repairs__status="Réparé"))
        rebutted = Count('repairs', filter=Q(repairs__status="Rebut"))
        packed = Count('repairs', filter=Q(repairs__checkout=True))
        queryset = Batch.objects.all().order_by('batch_number')
        queryset = queryset.annotate(repaired=repaired, packed=packed, rebutted=rebutted, total=Count('repairs'))
        values_list = (
            'batch_number', 'quantity', 'ecu_ref_base__reman_reference', 'repaired', 'rebutted', 'packed', 'total',
            'start_date', 'end_date', 'ecu_ref_base__ecu_type__technical_data', 'ecu_ref_base__ecu_type__hw_reference',
            'ecu_ref_base__ecu_type__supplier_oe', 'active', 'created_by__username', 'created_at'
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
        queryset = EcuType.objects.all().order_by('ecu_ref_base__reman_reference')
        values_list = (
            'ecumodel__oe_raw_reference', 'ecu_ref_base__reman_reference', 'technical_data', 'hw_reference',
            'supplier_oe', 'ecumodel__psa_barcode', 'ecumodel__former_oe_reference', 'ref_cal_out',
            'spare_part__code_produit', 'ref_psa_out', 'open_diag', 'ref_mat', 'ref_comp', 'cal_ktag', 'status'
        )
    fields = values_list
    values_list = queryset.values_list(*values_list).distinct()
    return header, fields, values_list


"""
##################################

Export Tools data to excel format

##################################
"""


def extract_tools(model):
    header = queryset = values_list = None
    if model == "suptech":
        header = [
            'DATE', 'QUI', 'XELON', 'ITEM', 'TIME', 'INFO', 'RMQ', 'ACTION/RETOUR', 'STATUS', 'DATE_LIMIT',
            'ACTION_LE', 'ACTION_PAR', 'DELAIS_EN_JOURS'
        ]
        fullname = Concat('modified_by__first_name', Value(' '), 'modified_by__last_name')
        day_number = ExtractDay(F('modified_at') - F('created_at')) + 1
        queryset = Suptech.objects.annotate(fullname=fullname, day_number=day_number).order_by('date')
        values_list = (
            'date', 'user', 'xelon', 'item', 'time', 'info', 'rmq', 'action', 'status', 'deadline', 'modified_at',
            'fullname', 'day_number'
        )
    if model == "bga_time":
        header = ['MACHINE', 'DATE', 'HEURE DEBUT', 'DUREE']
        queryset = BgaTime.objects.all()
        values_list = ('name', 'date', 'start_time', 'duration')
    fields = values_list
    values_list = queryset.values_list(*values_list).distinct()
    return header, fields, values_list
