from django.db.models.functions import Cast, TruncSecond, Concat, ExtractDay
from django.db.models import DateTimeField, CharField, Q, Count, Value, F

from psa.models import Corvet
from reman.models import Batch, Repair, EcuRefBase
from tools.models import Suptech, BgaTime

CORVET_DICT = {
    'xelon': [
        ('Dossier (XELON)', 'xelon__numero_de_dossier'), ('Produit (XELON)', 'xelon__modele_produit'),
        ('Vehicule (XELON)', 'xelon__modele_vehicule'), ('Date Retour (XELON)', 'xelon__date_retour')
    ],
    'data': [
        ('V.I.N.', 'vin'), ('DATE_DEBUT_GARANTIE', 'date_debut_garantie')
    ],
    'data_extra': [
        ('LIGNE_DE_PRODUIT', 'donnee_ligne_de_produit'), ('SILHOUETTE', 'donnee_silhouette'),
        ('GENRE_DE_PRODUIT', 'donnee_genre_de_produit'), ('MOTEUR', 'donnee_moteur'),
    ],
    'btel': [
        ('Modele NAV', 'prods__btel__name'), ('14X_BTEL_HARD', 'electronique_14x'),
        ('94X_BTEL_SOFT', 'electronique_94x')
    ],
    'btel_extra': [
        ('44X_BTEL_FOURN.NO.SERIE', 'electronique_44x'), ('64X_BTEL_FOURN.CODE', 'electronique_64x'),
        ('84X_BTEL_DOTE', 'electronique_84x'), ('Réf. Setplate', 'prods__btel__label_ref'),
        ('Niv.', 'prods__btel__level'), ('HW variant', 'prods__btel__extra'), ('DHB_HAUT_PARLEUR', 'attribut_dhb'),
        ('DRC_RECEPTEUR_RADIO', 'attribut_drc'), ('DUN_AMPLI_EQUALISEUR', 'attribut_dun'), ('DYR_BTA', 'attribut_dyr')
    ],
    'rad': [
        ('Modele RADIO', 'prods__radio__name'), ('14F_RADIO_HARD', 'electronique_14f'),
        ('94F_RADIO_SOFT', 'electronique_94f')
    ],
    'rad_extra': [
        ('44F_RADIO_FOURN.NO.SERIE', 'electronique_44f'), ('64F_RADIO_FOURN.CODE', 'electronique_64f'),
        ('84F_RADIO_DOTE', 'electronique_84f'), ('Réf. Setplate', 'prods__radio__label_ref'),
        ('Niv.', 'prods__radio__level'), ('HW variant', 'prods__radio__extra'), ('DHB_HAUT_PARLEUR', 'attribut_dhb'),
        ('DRC_RECEPTEUR_RADIO', 'attribut_drc'), ('DUN_AMPLI_EQUALISEUR', 'attribut_dun'), ('DYR_BTA', 'attribut_dyr')
    ],
    'emf': [
        ('Modèle Ecran Multi', 'prods__emf__name'), ('14L_EMF_HARD', 'electronique_14l'),
        ('44L_EMF_FOURN.NO.SERIE', 'electronique_44l'), ('54L_EMF_FOUN.DATE.FAB', 'electronique_54l'),
        ('84L_EMF_DOTE', 'electronique_84l'), ('94L_EMF_SOFT', 'electronique_94l')
    ],
    'cmb': [
        ('Modèle COMBINE', 'prods__cmb__name'), ('14K_CMB_HARD', 'electronique_14k'),
        ('54K_CMB_FOUN.DATE.FAB', 'electronique_54k'), ('94K_CMB_SOFT', 'electronique_94k')
    ],
    'com200x': [
        ('Modele COM200x', 'prods__hdc__name'), ('Marque COM200x', 'prods__hdc__supplier_oe'),
        ('Ref HW COM200x', 'electronique_16p'),
    ],
    'cmm': [
        ('Modèle ECU', 'prods__cmm__name'),
        ('14A_CMM_HARD', 'electronique_14a'), ('34A_CMM_SOFT_LIVRE', 'electronique_34a'),
        ('94A_CMM_SOFT', 'electronique_94a'), ('44A_CMM_FOURN.NO.SERIE', 'electronique_44b'),
        ('54A_CMM_FOURN.DATE.FAB', 'electronique_54b'), ('64A_CMM_FOURN.CODE', 'electronique_64b'),
        ('84A_CMM_DOTE', 'electronique_84a'), ('P4A_CMM_EOBD', 'electronique_p4a')
    ],
    'bsi': [
        ('Modèle B.S.I.', 'prods__bsi__name'), ('HW', 'prods__bsi__hw'),
        ('SW', 'prods__bsi__sw'),
        ('14B_BSI_HARD', 'electronique_14b'),
        ('94B_BSI_SOFT', 'electronique_94b'), ('44B_BSI_FOURN.NO.SERIE', 'electronique_44b'),
        ('54B_BSI_FOURN.DATE.FAB', 'electronique_54b'), ('64B_BSI_FOURN.CODE', 'electronique_64b'),
        ('84B_BSI_DOTE', 'electronique_84b')
    ],
    'bsm': [
        ('Modele BSM', 'prods__bsm__name'), ('Marque BSM', 'prods__bsm__supplier_oe'),
        ('Ref HW BSM', 'electronique_16b'),
    ],
    'cvm': [
        ('Modèle CVM_2', 'prods__cvm2__name'),
        ('12Y_CVM2_2_HARD', 'electronique_12y'), ('92Y_CVM2_2_SOFT', 'electronique_92y')
    ],
    'dae': [
        ('16L_DAE_HARD', 'electronique_16l'),
        ('96L_DAE_SOFT', 'electronique_96l')
    ]
}

XELON_LIST = [
    ('Dossier (XELON)', 'xelon__numero_de_dossier'), ('Produit (XELON)', 'xelon__modele_produit'),
    ('Vehicule (XELON)', 'xelon__modele_vehicule'), ('Date Retour (XELON)', 'xelon__date_retour')
]

DATA_LIST = [
    ('V.I.N.', 'vin'), ('DATE_DEBUT_GARANTIE', 'date_debut_garantie'),
    ('LIGNE_DE_PRODUIT', 'donnee_ligne_de_produit'), ('SILHOUETTE', 'donnee_silhouette'),
    ('GENRE_DE_PRODUIT', 'donnee_genre_de_produit'), ('MOTEUR', 'donnee_moteur'),
]

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

    ('Modele BSM', 'prods__bsm__name'), ('Marque BSM', 'prods__bsm__supplier_oe'),
    ('Ref HW BSM', 'electronique_16b'),
    ('Modele CVM2', 'prods__cvm2__name'), ('Marque CVM2', 'prods__cvm2__supplier_oe'),
    ('12Y_CVM2_2_HARD', 'electronique_12y'), ('92Y_CVM2_2_SOFT', 'electronique_92y')
]

PRODS_XELON_LIST = [
    ('NAV (XELON)', 'prods__btel__xelon_name'),
    ('Modele NAV', 'prods__btel__name'), ('Marque NAV', 'prods__btel__supplier_oe'),
    ('Ref HW NAV', 'electronique_14x'), ('RADIO (XELON)', 'prods__radio__xelon_name'),
    ('Modele RADIO', 'prods__radio__name'), ('Marque RADIO', 'prods__radio__supplier_oe'),
    ('Ref HW RADIO', 'electronique_14f'), ('EMF (XELON)', 'prods__emf__xelon_name'),
    ('Modele EMF', 'prods__emf__name'), ('Marque EMF', 'prods__emf__supplier_oe'),
    ('Ref HW EMF', 'electronique_14l'), ('TDB (XELON)', 'prods__cmb__xelon_name'),
    ('Modele TDB', 'prods__cmb__name'), ('Marque TDB', 'prods__cmb__supplier_oe'),
    ('Ref HW TDB', 'electronique_14k'), ('ECU (XELON)', 'prods__cmm__xelon_name'),
    ('Modele ECU MOTEUR', 'prods__cmm__name'), ('Marque ECU MOTEUR', 'prods__cmm__supplier_oe'),
    ('Ref HW ECU MOTEUR', 'electronique_14a'), ('BSI (XELON)', 'prods__bsi__xelon_name'),
    ('Modele BSI', 'prods__bsi__name'), ('Marque BSI', 'prods__bsi__supplier_oe'),
    ('Ref HW BSI', 'electronique_14b'), ('COM200X (XELON)', 'prods__hdc__xelon_name'),
    ('Modele COM200x', 'prods__hdc__name'), ('Marque COM200x', 'prods__hdc__supplier_oe'),
    ('Ref HW COM200x', 'electronique_16p'), ('BSM (XELON', 'prods__bsm__xelon_name'),
    ('Modele BSM', 'prods__bsm__name'), ('Marque BSM', 'prods__bsm__supplier_oe'),
    ('Ref HW BSM', 'electronique_16b'),
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
    prod_dict = {
        'btel': {'electronique_14x__exact': ''}, 'rad': {'electronique_14f__exact': ''},
        'ecu': {'electronique_14a__exact': ''}, 'bsi': {'electronique_14b__exact': ''},
        'com200x': {'electronique_16p__exact': ''}, 'bsm': {'electronique_16p__exact': ''},
        'cvm': {'electronique_12y__exact': ''}, 'dae': {'electronique_16l__exact': ''},
        'emf': {'electronique_16l__exact': ''}, 'cmb': {'electronique_14k__exact': ''}
    }
    product = kwargs.get('product', 'bsi')
    data_list = CORVET_DICT['xelon'] + CORVET_DICT['data']
    for col in kwargs.get('columns', []):
        data_list += CORVET_DICT.get(col, [])
    queryset = Corvet.objects.all().annotate(
        date_debut_garantie=Cast(TruncSecond('donnee_date_debut_garantie', DateTimeField()), CharField()))
    if kwargs.get('tag', None):
        queryset = queryset.filter(opts__tag=kwargs.get('tag'))
    if kwargs.get('vins', None):
        vin_list = kwargs.get('vins').split('\r\n')
        queryset = queryset.filter(vin__in=vin_list)
    if kwargs.get('xelon_model', None):
        queryset = queryset.select_related().filter(xelon__modele_produit__startswith=kwargs.get('xelon_model'))
    if kwargs.get('xelon_vehicle', None):
        queryset = queryset.select_related().filter(xelon__modele_vehicule__startswith=kwargs.get('xelon_vehicle'))
    if kwargs.get('start_date', None):
        queryset = queryset.filter(donnee_date_debut_garantie__gte=kwargs.get('start_date'))
    if kwargs.get('end_date', None):
        queryset = queryset.filter(donnee_date_debut_garantie__lte=kwargs.get('end_date'))
    header, values_list = get_header_fields(data_list)
    if prod_dict.get(product):
        queryset = queryset.exclude(**prod_dict.get(product))
    elif product == "xelon":
        header, values_list = get_header_fields(XELON_LIST + DATA_LIST + PRODS_XELON_LIST)
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
