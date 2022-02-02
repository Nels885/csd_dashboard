from django.db.models.functions import Cast, TruncSecond, Concat, ExtractDay
from django.db.models import DateTimeField, CharField, Q, Count, Value, F

from squalaetp.models import Xelon
from psa.models import Corvet
from reman.models import Batch, Repair, EcuRefBase
from tools.models import Suptech, BgaTime

CORVET_DICT = {
    'xelon': [
        ('Dossier (XELON)', 'numero_de_dossier'), ('V.I.N. (XELON)', 'vin'), ('Produit (XELON)', 'modele_produit'),
        ('Vehicule (XELON)', 'modele_vehicule'), ('Date Retour (XELON)', 'date_retour')
    ],
    'data': [
        ('DATE_DEBUT_GARANTIE', 'date_debut_garantie'), ('LIGNE_DE_PRODUIT', 'corvet__donnee_ligne_de_produit'),
        ('SILHOUETTE', 'corvet__donnee_silhouette'), ('GENRE_DE_PRODUIT', 'corvet__donnee_genre_de_produit'),
        ('MOTEUR', 'corvet__donnee_moteur'),
    ],
    'btel': [
        ('Modele NAV', 'corvet__prods__btel__name'), ('Réf. Setplate', 'corvet__prods__btel__label_ref'),
        ('Niv.', 'corvet__prods__btel__level'), ('HW variant', 'corvet__prods__btel__extra'),
        ('DHB_HAUT_PARLEUR', 'corvet__attribut_dhb'), ('DRC_RECEPTEUR_RADIO', 'corvet__attribut_drc'),
        ('DUN_AMPLI_EQUALISEUR', 'corvet__attribut_dun'),
        ('DYR_BTA', 'corvet__attribut_dyr'), ('14X_BTEL_HARD', 'corvet__electronique_14x'),
        ('44X_BTEL_FOURN.NO.SERIE', 'corvet__electronique_44x'), ('64X_BTEL_FOURN.CODE', 'corvet__electronique_64x'),
        ('84X_BTEL_DOTE', 'corvet__electronique_84x'), ('94X_BTEL_SOFT', 'corvet__electronique_94x')
    ],
    'rad': [
        ('Modele RADIO', 'corvet__prods__radio__name'), ('Réf. Setplate', 'corvet__prods__radio__label_ref'),
        ('Niv.', 'corvet__prods__radio__level'), ('HW variant', 'corvet__prods__radio__extra'),
        ('DHB_HAUT_PARLEUR', 'corvet__attribut_dhb'), ('DRC_RECEPTEUR_RADIO', 'corvet__attribut_drc'),
        ('DUN_AMPLI_EQUALISEUR', 'corvet__attribut_dun'),
        ('DYR_BTA', 'corvet__attribut_dyr'), ('14F_RADIO_HARD', 'corvet__electronique_14f'),
        ('44F_RADIO_FOURN.NO.SERIE', 'corvet__electronique_44f'), ('64F_RADIO_FOURN.CODE', 'corvet__electronique_64f'),
        ('84F_RADIO_DOTE', 'corvet__electronique_84f'), ('94F_RADIO_SOFT', 'corvet__electronique_94f')
    ],
    'emf': [
        ('Modèle Ecran Multi', 'corvet__prods__emf__name'), ('14L_EMF_HARD', 'corvet__electronique_14l'),
        ('44L_EMF_FOURN.NO.SERIE', 'corvet__electronique_44l'), ('54L_EMF_FOUN.DATE.FAB', 'corvet__electronique_54l'),
        ('84L_EMF_DOTE', 'corvet__electronique_84l'), ('94L_EMF_SOFT', 'corvet__electronique_94l')
    ],
    'cmb': [
        ('Modèle COMBINE', 'corvet__prods__cmb__name'), ('14K_CMB_HARD', 'corvet__electronique_14k'),
        ('54K_CMB_FOUN.DATE.FAB', 'corvet__electronique_54k'), ('94K_CMB_SOFT', 'corvet__electronique_94k')
    ],
    'cmm': [
        ('Modèle ECU', 'corvet__prods__cmm__name'),
        ('14A_CMM_HARD', 'corvet__electronique_14a'), ('34A_CMM_SOFT_LIVRE', 'corvet__electronique_34a'),
        ('94A_CMM_SOFT', 'corvet__electronique_94a'), ('44A_CMM_FOURN.NO.SERIE', 'corvet__electronique_44b'),
        ('54A_CMM_FOURN.DATE.FAB', 'corvet__electronique_54b'), ('64A_CMM_FOURN.CODE', 'corvet__electronique_64b'),
        ('84A_CMM_DOTE', 'corvet__electronique_84a'), ('P4A_CMM_EOBD', 'corvet__electronique_p4a')
    ],
    'bsi': [
        ('Modèle B.S.I.', 'corvet__prods__bsi__name'), ('HW', 'corvet__prods__bsi__hw'),
        ('SW', 'corvet__prods__bsi__sw'),
        ('14B_BSI_HARD', 'corvet__electronique_14b'),
        ('94B_BSI_SOFT', 'corvet__electronique_94b'), ('44B_BSI_FOURN.NO.SERIE', 'corvet__electronique_44b'),
        ('54B_BSI_FOURN.DATE.FAB', 'corvet__electronique_54b'), ('64B_BSI_FOURN.CODE', 'corvet__electronique_64b'),
        ('84B_BSI_DOTE', 'corvet__electronique_84b')
    ],
    'cvm': [
        ('Modèle CVM_2', 'corvet__prods__cvm2__name'),
        ('12Y_CVM2_2_HARD', 'corvet__electronique_12y'), ('92Y_CVM2_2_SOFT', 'corvet__electronique_92y')
    ],
    'dae': [
        ('16L_DAE_HARD', 'corvet__electronique_16l'),
        ('96L_DAE_SOFT', 'corvet__electronique_96l')
    ]
}

XELON_LIST = [
    ('Dossier (XELON)', 'numero_de_dossier'), ('V.I.N. (XELON)', 'vin'), ('Produit (XELON)', 'modele_produit'),
    ('Vehicule (XELON)', 'modele_vehicule'), ('Date Retour (XELON)', 'date_retour')
]

DATA_LIST = [
    ('DATE_DEBUT_GARANTIE', 'date_debut_garantie'), ('LIGNE_DE_PRODUIT', 'corvet__donnee_ligne_de_produit'),
    ('SILHOUETTE', 'corvet__donnee_silhouette'), ('GENRE_DE_PRODUIT', 'corvet__donnee_genre_de_produit'),
    ('MOTEUR', 'corvet__donnee_moteur'),
]

# PRODS_LIST = [
#     ('Modele NAV', 'corvet__prods__btel__name'), ('Marque NAV', 'corvet__prods__btel__supplier_oe'),
#     ('Ref HW NAV', 'corvet__electronique_14x'),
#     ('Modele RADIO', 'corvet__prods__radio__name'), ('Marque RADIO', 'corvet__prods__radio__supplier_oe'),
#     ('Ref HW RADIO', 'corvet__electronique_14f'),
#     ('Modele EMF', 'corvet__prods__emf__name'), ('Marque EMF', 'corvet__prods__emf__supplier_oe'),
#     ('Ref HW EMF', 'corvet__electronique_14l'),
#     ('Modele TDB', 'corvet__prods__cmb__name'), ('Marque TDB', 'corvet__prods__cmb__supplier_oe'),
#     ('Ref HW TDB', 'corvet__electronique_14k'),
#     ('Modele ECU MOTEUR', 'corvet__prods__cmm__name'), ('Marque ECU MOTEUR', 'corvet__prods__cmm__supplier_oe'),
#     ('Ref HW ECU MOTEUR', 'corvet__electronique_14a'),
#     ('Modele BSI', 'corvet__prods__bsi__name'), ('Marque BSI', 'corvet__prods__bsi__supplier_oe'),
#     ('Ref HW BSI', 'corvet__electronique_14b'),
#     ('Modele COM200x', 'corvet__prods__hdc__name'), ('Marque COM200x', 'corvet__prods__hdc__supplier_oe'),
#     ('Ref HW COM200x', 'corvet__electronique_16p'),
#     ('Modele BSM', 'corvet__prods__bsm__name'), ('Marque BSM', 'corvet__prods__bsm__supplier_oe'),
#     ('Ref HW BSM', 'corvet__electronique_16b'),
#     ('Modele CVM2', 'corvet__prods__cvm2__name'), ('Marque CVM2', 'corvet__prods__cvm2__supplier_oe'),
#     ('12Y_CVM2_2_HARD', 'corvet__electronique_12y'), ('92Y_CVM2_2_SOFT', 'corvet__electronique_92y')
# ]

PRODS_LIST = [
    ('V.I.N.', 'vin'),
    ('Modele NAV', 'prods__btel__name'), ('Marque NAV', 'prods__btel__supplier_oe'),
    ('Ref HW NAV', 'electronique_14x'),
    ('Modele RADIO', 'prods__radio__name'), ('Marque RADIO', 'prods__radio__supplier_oe'),
    ('Ref HW RADIO', 'electronique_14f'),
    ('Modele EMF', 'prods__emf__name'), ('Marque EMF', 'prods__emf__supplier_oe'),
    ('Ref HW EMF', 'electronique_14l'),
    ('Modele TDB', 'prods__cmb__name'), ('Marque TDB', 'prods__cmb__supplier_oe'),
    ('Ref HW TDB', 'electronique_14k'),
    ('Modele ECU MOTEUR', 'prods__cmm__name'), ('Marque ECU MOTEUR', 'prods__cmm__supplier_oe'),
    ('Ref HW ECU MOTEUR', 'electronique_14a'),
    ('Modele BSI', 'prods__bsi__name'), ('Marque BSI', 'prods__bsi__supplier_oe'),
    ('Ref HW BSI', 'electronique_14b'),
    ('Modele COM200x', 'prods__hdc__name'), ('Marque COM200x', 'prods__hdc__supplier_oe'),
    ('Ref HW COM200x', 'electronique_16p'),
    ('Modele BSM', 'prods__bsm__name'), ('Marque BSM', 'prods__bsm__supplier_oe'),
    ('Ref HW BSM', 'electronique_16b'),
    ('Modele CVM2', 'prods__cvm2__name'), ('Marque CVM2', 'prods__cvm2__supplier_oe'),
    ('12Y_CVM2_2_HARD', 'electronique_12y'), ('92Y_CVM2_2_SOFT', 'electronique_92y')
]

PRODS_XELON_LIST = [
    ('NAV (XELON)', 'corvet__prods__btel__xelon_name'),
    ('Modele NAV', 'corvet__prods__btel__name'), ('Marque NAV', 'corvet__prods__btel__supplier_oe'),
    ('Ref HW NAV', 'corvet__electronique_14x'), ('RADIO (XELON)', 'corvet__prods__radio__xelon_name'),
    ('Modele RADIO', 'corvet__prods__radio__name'), ('Marque RADIO', 'corvet__prods__radio__supplier_oe'),
    ('Ref HW RADIO', 'corvet__electronique_14f'), ('EMF (XELON)', 'corvet__prods__emf__xelon_name'),
    ('Modele EMF', 'corvet__prods__emf__name'), ('Marque EMF', 'corvet__prods__emf__supplier_oe'),
    ('Ref HW EMF', 'corvet__electronique_14l'), ('TDB (XELON)', 'corvet__prods__cmb__xelon_name'),
    ('Modele TDB', 'corvet__prods__cmb__name'), ('Marque TDB', 'corvet__prods__cmb__supplier_oe'),
    ('Ref HW TDB', 'corvet__electronique_14k'), ('ECU (XELON)', 'corvet__prods__cmm__xelon_name'),
    ('Modele ECU MOTEUR', 'corvet__prods__cmm__name'), ('Marque ECU MOTEUR', 'corvet__prods__cmm__supplier_oe'),
    ('Ref HW ECU MOTEUR', 'corvet__electronique_14a'), ('BSI (XELON)', 'corvet__prods__bsi__xelon_name'),
    ('Modele BSI', 'corvet__prods__bsi__name'), ('Marque BSI', 'corvet__prods__bsi__supplier_oe'),
    ('Ref HW BSI', 'corvet__electronique_14b'), ('COM200X (XELON)', 'corvet__prods__hdc__xelon_name'),
    ('Modele COM200x', 'corvet__prods__hdc__name'), ('Marque COM200x', 'corvet__prods__hdc__supplier_oe'),
    ('Ref HW COM200x', 'corvet__electronique_16p'), ('BSM (XELON', 'corvet__prods__bsm__xelon_name'),
    ('Modele BSM', 'corvet__prods__bsm__name'), ('Marque BSM', 'corvet__prods__bsm__supplier_oe'),
    ('Ref HW BSM', 'corvet__electronique_16b'),
]


def get_header_fields(prod_list):
    header = [value_tuple[0] for value_tuple in prod_list]
    fields = [value_tuple[1] for value_tuple in prod_list]
    return header, fields


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


def extract_corvet(*args, **kwargs):
    product = kwargs.get('product', 'bsi')
    data_list = CORVET_DICT['xelon'] + CORVET_DICT['data']
    for col in kwargs.get('columns', []):
        data_list += CORVET_DICT.get(col, [])
    queryset = Xelon.objects.filter(
        date_retour__isnull=False, corvet__isnull=False).order_by('-numero_de_dossier').annotate(
        date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
    )
    if kwargs.get('xelon_model', None):
        queryset = queryset.filter(modele_produit__startswith=kwargs.get('xelon_model'))
    if kwargs.get('xelon_vehicle', None):
        queryset = queryset.filter(modele_vehicule__startswith=kwargs.get('xelon_vehicle'))
    if kwargs.get('start_date', None):
        queryset = queryset.filter(corvet__donnee_date_debut_garantie__gte=kwargs.get('start_date'))
    if kwargs.get('end_date', None):
        queryset = queryset.filter(corvet__donnee_date_debut_garantie__lte=kwargs.get('end_date'))
    header, values_list = get_header_fields(data_list)
    if product == "ecu":
        queryset = queryset.exclude(corvet__electronique_14a__exact='')
    elif product == "bsi":
        queryset = queryset.exclude(corvet__electronique_14b__exact='')
    elif product == "com200x":
        queryset = queryset.exclude(corvet__electronique_16p__exact='')
    elif product == "bsm":
        queryset = queryset.exclude(corvet__electronique_16p__exact='')
    elif product == "cvm":
        queryset = queryset.exclude(corvet__electronique_12y__exact='')
    elif product == "dae":
        queryset = queryset.exclude(corvet__electronique_16l__exact='')
    elif product == "emf":
        queryset = queryset.exclude(corvet__electronique_14l__exact='')
    elif product == "cmb":
        queryset = queryset.exclude(corvet__electronique_14k__exact='')
    elif product == "nac":
        queryset = queryset.filter(corvet__attribut_drc="NA")
    elif product == "rcc":
        queryset = queryset.filter(corvet__attribut_drc="RC")
    elif product == "rtx":
        queryset = queryset.filter(corvet__attribut_drc__in=["T3", "T4", "T6"])
    elif product == "rdx":
        queryset = queryset.exclude(corvet__electronique_14f='')
    elif product == "smeg":
        queryset = queryset.filter(corvet__attribut_drc="SA")
    elif product == "rneg":
        queryset = queryset.filter(corvet__attribut_drc="RN")
    elif product == "ng4":
        queryset = queryset.filter(corvet__attribut_drc="G4")
    elif product == "icare":
        # header, values_list = get_header_fields(XELON_LIST + DATA_LIST + PRODS_LIST)
        # queryset = queryset.filter(corvet__isnull=False, corvet__opts__tag="ICARE")
        header, values_list = get_header_fields(PRODS_LIST)
        queryset = Corvet.objects.filter(opts__tag="ICARE")
    elif product == "all":
        header, values_list = get_header_fields(XELON_LIST + DATA_LIST + PRODS_LIST)
        queryset = queryset.filter(corvet__isnull=False)
    elif product == "xelon":
        header, values_list = get_header_fields(XELON_LIST + DATA_LIST + PRODS_XELON_LIST)
        queryset = queryset.filter(corvet__isnull=False)
    # elif product == 'corvet':
    #     header = [
    #         'V.I.N.', 'DATE_DEBUT_GARANTIE', 'DATE_ENTREE_MONTAGE', 'LIGNE_DE_PRODUIT', 'MARQUE_COMMERCIALE',
    #         'SILHOUETTE', 'GENRE_DE_PRODUIT', 'DDO', 'DGM', 'DHB', 'DHG', 'DJQ', 'DJY', 'DKX', 'DLX', 'DOI', 'DQM',
    #         'DQS', 'DRC', 'DRT', 'DTI', 'DUN', 'DWL', 'DWT', 'DXJ', 'DYB', 'DYM', 'DYR', 'DZV', 'GG8', '14F', '14J',
    #         '14K', '14L', '14R', '14X', '19Z', '44F', '44L', '44X', '54F', '54K', '54L', '84F', '84L', '84X', '94F',
    #         '94L', '94X', 'DAT', 'DCX', '19H', '49H', '64F', '64X', '69H', '89H', '99H', '14A', '34A', '44A', '54A',
    #         '64A', '84A', '94A', 'P4A', 'MOTEUR', 'TRANSMISSION', '10', '14B', '20', '44B', '54B', '64B', '84B', '94B',
    #         '16P', '46P', '56P', '66P', '16B', '46B', '56B', '66B', '86B', '96B'
    #     ]
    #     queryset = Corvet.objects.all()
    #     values_list = tuple([field.name for col_nb, field in enumerate(Corvet._meta.fields)
    #                          if col_nb < len(header)])
    fields = values_list
    values_list = queryset.values_list(*values_list).distinct()[:30000]
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
            'Date_de_fin', 'Type_ECU', 'HW_Reference', 'Fabriquant', 'Actif', 'Ajoute par', 'Ajoute le'
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
            'Code_barre', 'Code_defaut', 'Libelle_defaut', 'Commentaires_action', 'status', 'Controle_qualite',
            'Date_de_cloture', 'Modifie_par', 'Modifie_le', 'Cree par', 'Cree_le'
        ]
        queryset = Repair.objects.all().order_by('identify_number')
        values_list = (
            'identify_number', 'batch__batch_number', 'batch__ecu_ref_base__reman_reference',
            'batch__ecu_ref_base__ecu_type__technical_data', 'batch__ecu_ref_base__ecu_type__supplier_oe',
            'batch__ecu_ref_base__ecu_type__hw_reference', 'barcode', 'default__code', 'default__description',
            'comment', 'status', 'quality_control', 'closing_date', 'modified_by__username', 'modified_at',
            'created_at', 'created_by__username',
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
