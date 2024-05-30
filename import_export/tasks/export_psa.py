from ast import literal_eval

from django.db.models.functions import Cast, TruncSecond
from django.db.models import DateTimeField, CharField

from utils.file.export_task import ExportExcelTask
from psa.models import Corvet, CorvetChoices
from psa.templatetags.corvet_tags import get_corvet
from psa.choices import BTEL_PRODUCT_CHOICES


INFO_DICT = {
    'xelon': {'label': 'Xelon', 'data': [
        ('Dossier (XELON)', 'xelon__numero_de_dossier'), ('Produit (XELON)', 'xelon__modele_produit'),
        ('Vehicule (XELON)', 'xelon__modele_vehicule'), ('Date Retour (XELON)', 'xelon__date_retour')
    ]},
    'data': {'label': 'Donnée', 'data': [
        ('V.I.N.', 'vin'), ('DATE_DEBUT_GARANTIE', 'date_debut_garantie')
    ]},
    'data_extra': {'label': 'Info Véhicule', 'data': [
        ('MARQUE_COMMERCIALE', 'donnee_marque_commerciale'),
        ('LIGNE_DE_PRODUIT', 'donnee_ligne_de_produit'), ('SILHOUETTE', 'donnee_silhouette'),
        ('GENRE_DE_PRODUIT', 'donnee_genre_de_produit'), ('MOTEUR', 'donnee_moteur'),
        ('TRANSMISSION', 'donnee_transmission')
    ]},
    'audio_cfg': {'label': 'Config Audio', 'data': [
        ('DHB_HAUT_PARLEUR', 'attribut_dhb'), ('DRC_RECEPTEUR_RADIO', 'attribut_drc'),
        ('DUN_AMPLI_EQUALISEUR', 'attribut_dun'), ('DYR_BTA', 'attribut_dyr')
    ]},
    'extra_ecu': {'label': 'Extra ECU', 'data': [
        ('Numero de dossier', 'xelon__numero_de_dossier'), ('V.I.N.', 'vin'),
        ('Modele produit', 'xelon__modele_produit'), ('Modele vehicule', 'xelon__modele_vehicule'),
        ('DATE_DEBUT_GARANTIE', 'donnee_date_debut_garantie'), ('14A_CMM_HARD', 'electronique_14a'),
        ('34A_CMM_SOFT_LIVRE', 'electronique_34a'), ('94A_CMM_SOFT', 'electronique_94a'),
        ('44A_CMM_FOURN.NO.SERIE', 'electronique_44a'), ('54A_CMM_FOURN.DATE.FAB', 'electronique_54a'),
        ('64A_CMM_FOURN.CODE', 'electronique_64a'), ('84A_CMM_DOTE', 'electronique_84a'),
        ('P4A_CMM_EOBD', 'electronique_p4a')
    ]},
}

ENGINE_DICT = {
    'cmm': {'label': 'ECU', 'filter': {'electronique_14a__exact': ''}, 'data': [
        ('Modèle ECU', 'prods__cmm__name'),
        ('14A_CMM_HARD', 'electronique_14a'), ('34A_CMM_SOFT_LIVRE', 'electronique_34a'),
        ('94A_CMM_SOFT', 'electronique_94a')
    ]},
    'cmm_extra': {'label': 'ECU Extra', 'data': [
        ('44A_CMM_FOURN.NO.SERIE', 'electronique_44b'),
        ('54A_CMM_FOURN.DATE.FAB', 'electronique_54b'), ('64A_CMM_FOURN.CODE', 'electronique_64b'),
        ('84A_CMM_DOTE', 'electronique_84a'), ('P4A_CMM_EOBD', 'electronique_p4a')
    ]},
    'bsm': {'label': 'BSM', 'filter': {'electronique_16p__exact': ''}, 'data': [
        ('Modele BSM', 'prods__bsm__name'), ('Marque BSM', 'prods__bsm__supplier_oe'),
        ('Ref HW BSM', 'electronique_16b'),
    ]},
    'dmtx': {'label': 'DMTX', 'filter': {'electronique_11q__exact': ''}, 'data': [
        ('Modèle DMTX', 'prods__dmtx__name'),
        ('11Q_DMTX_HARD', 'electronique_11q')
    ]},
    'dmtx_extra': {'label': 'DMTX Extra', 'data': [
        ('41Q_DMTX_FOURN.NO.SERIE', 'electronique_41q'), ('51Q_DMTX_FOURN.DATE.FAB', 'electronique_51q'),
        ('61Q_DMTX_FOURN.CODE', 'electronique_61q'), ('91Q_DMTX_SOFT', 'electronique_91q'),
        ('Réf. Setplate DMTX', 'prods__dmtx__label_ref'),
    ]},
    'bpga': {'label': 'BPGA', 'filter': {'electronique_11n__exact': ''}, 'data': [
        ('Modèle BPGA', 'prods__bpga__name'), ('Marque BPGA', 'prods__bpga__supplier_oe'),
        ('11N_BPGA_HARD', 'electronique_11n'),
    ]},
    'bpga_extra': {'label': 'BPGA Extra', 'data': [
        ('41N_BPGA_FOURN.NO.SERIE', 'electronique_41n'), ('51N_BPGA_FOURN.DATE.FAB', 'electronique_51n'),
        ('61N_BPGA_FOURN.CODE', 'electronique_61n'),
    ]},
}

INTERIOR_DICT = {
    'bsi': {'label': 'BSI', 'filter': {'electronique_14b__exact': ''}, 'data': [
        ('Modèle B.S.I.', 'prods__bsi__name'), ('14B_BSI_HARD', 'electronique_14b'),
        ('94B_BSI_SOFT', 'electronique_94b')
    ]},
    'bsi_extra': {'label': 'BSI Extra', 'data': [
        ('44B_BSI_FOURN.NO.SERIE', 'electronique_44b'), ('54B_BSI_FOURN.DATE.FAB', 'electronique_54b'),
        ('64B_BSI_FOURN.CODE', 'electronique_64b'), ('84B_BSI_DOTE', 'electronique_84b'), ('HW', 'prods__bsi__hw'),
        ('SW', 'prods__bsi__sw'),
    ]},
    'btel': {'label': 'NAV', 'filter': {'electronique_14x__exact': ''}, 'data': [
        ('Modele NAV', 'prods__btel__name'), ('14X_BTEL_HARD', 'electronique_14x'),
        ('94X_BTEL_SOFT', 'electronique_94x')
    ]},
    'btel_extra': {'label': 'NAV Extra', 'data': [
        ('44X_BTEL_FOURN.NO.SERIE', 'electronique_44x'), ('64X_BTEL_FOURN.CODE', 'electronique_64x'),
        ('84X_BTEL_DOTE', 'electronique_84x'), ('Réf. Setplate', 'prods__btel__label_ref'),
        ('Niv.', 'prods__btel__level'), ('HW variant', 'prods__btel__extra')
    ]},
    'rad': {'label': 'RADIO', 'filter': {'electronique_14f__exact': ''}, 'data': [
        ('Modele RADIO', 'prods__radio__name'), ('14F_RADIO_HARD', 'electronique_14f'),
        ('94F_RADIO_SOFT', 'electronique_94f')
    ]},
    'rad_extra': {'label': 'RADIO Extra', 'data': [
        ('44F_RADIO_FOURN.NO.SERIE', 'electronique_44f'), ('64F_RADIO_FOURN.CODE', 'electronique_64f'),
        ('84F_RADIO_DOTE', 'electronique_84f'), ('Réf. Setplate', 'prods__radio__label_ref'),
        ('Niv.', 'prods__radio__level'), ('HW variant', 'prods__radio__extra')
    ]},
    'ivi': {'label': 'IVI', 'filter': {'electronique_1m2__exact': ''}, 'data': [
        ('1M2_IVI_HARD', 'electronique_1m2'), ('3M2_IVI_SOFT', 'electronique_3m2')
    ]},
    'ivi_extra': {'label': 'IVI Extra', 'data': [
        ('4M2_IVI_FOURN.NO.SERIE', 'electronique_4m2'), ('5M2_IVI_FOUN.DATE.FAB.', 'electronique_5m2'),
        ('6M2_IVI_FOURN.CODE', 'electronique_6m2'), ('8M2_IVI_???', 'electronique_8m2'),
        ('XM2_IVI_DATA_LIBRARY', 'electronique_xm2')
    ]},
    'bsrf': {'label': 'BSRF', 'filter': {'electronique_1l9__exact': ''}, 'data': [
        ('1L9_BSRF_HARD', 'electronique_1l9'), ('3L9_BSRF_SOFT', 'electronique_3l9')
    ]},
    'bsrf_extra': {'label': 'BSRF Extra', 'data': [
        ('4L9_BSRF_FOURN.NO.SERIE', 'electronique_4l9'), ('6L9_BSRF_FOURN.CODE', 'electronique_6l9'),
        ('8L9_BSRF_???', 'electronique_8l9'), ('9L9_BSRF_???', 'electronique_9l9'),
        ('KL9_BSRF_NUMERO.IMEI', 'electronique_kl9'), ('ML9_BSRF_NUMERO.IMSI', 'electronique_ml9'),
        ('RL9_BSRF_NUMERO.ICCID', 'electronique_rl9'), ('YL9_BSRF_VEHICLE.APP', 'electronique_yl9')
    ]},
    'fmux': {'label': 'FMUX', 'filter': {'electronique_19z__exact': ''}, 'data': [
        ('19Z_FMUX_HARD', 'electronique_19z')
    ]},
    'emf': {'label': 'DISPLAY', 'fitler': {'electronique_16l__exact': ''}, 'data': [
        ('Modèle Ecran Multi', 'prods__emf__name'), ('14L_EMF_HARD', 'electronique_14l'),
        ('44L_EMF_FOURN.NO.SERIE', 'electronique_44l'), ('54L_EMF_FOUN.DATE.FAB', 'electronique_54l'),
        ('84L_EMF_DOTE', 'electronique_84l'), ('94L_EMF_SOFT', 'electronique_94l')
    ]},
    'cmb': {'label': 'COMBINE', 'filter': {'electronique_14k__exact': ''}, 'data': [
        ('Modèle COMBINE', 'prods__cmb__name'), ('14K_CMB_HARD', 'electronique_14k'),
        ('54K_CMB_FOUN.DATE.FAB', 'electronique_54k'), ('94K_CMB_SOFT', 'electronique_94k')
    ]},
    'com200x': {'label': 'COM200x', 'filter': {'electronique_16p__exact': ''}, 'data': [
        ('Modele COM200x', 'prods__hdc__name'), ('Marque COM200x', 'prods__hdc__supplier_oe'),
        ('Ref HW COM200x', 'electronique_16p'),
    ]},
    'vmf': {'label': 'VMF', 'filter': {'electronique_11m__exact': ''}, 'data': [
        ('Modèle VMF', 'prods__vmf__name'),
        ('11M_VMF_HARD', 'electronique_11m')
    ]},
}

SECURITY_DICT = {
    'cvm': {'label': 'CVM', 'filter': {'electronique_12y__exact': ''}, 'data': [
        ('Modèle CVM2', 'prods__cvm2__name'),
        ('12Y_CVM2_2_HARD', 'electronique_12y'), ('92Y_CVM2_2_SOFT', 'electronique_92y')
    ]},
    'cvm_extra': {'label': 'CVM Extra', 'data': [
        ('T2Y_CVM2_2_CODE', 'electronique_t2y'), ('Réf. Setplate CVM2', 'prods__cvm2__label_ref'),
        ('Complément CVM2', 'prods__cvm2__extra')
    ]},
    'artiv': {'label': 'ARTIV', 'filter': {'electronique_19k__exact': ''}, 'data': [
        ('19K_ARTIV_HARD', 'electronique_19k'), ('99K_ARTIV_SOFT', 'electronique_99k')
    ]},
    'artiv_extra': {'label': 'ARTIV Extra', 'data': [
        ('69K_ARTIV_FOURN.CODE', 'electronique_69k'), ('49K_ARTIV_FOURN.NO.SERIE', 'electronique_49k'),
        ('59K_ARTIV_FOURN.DATE.FAB', 'electronique_59k')
    ]},
    'dae': {'label': 'DAE', 'filter': {'electronique_16l__exact': ''}, 'data': [
        ('16L_DAE_HARD', 'electronique_16l'), ('96L_DAE_SOFT', 'electronique_96l')
    ]},
    'abs_esp': {'label': 'ABS/ESP', 'filter': {'electronique_14p__exact': ''}, 'data': [
        ('14P_FREIN_HARD', 'electronique_14p'), ('94P_FREIN_SOFT', 'electronique_94p'),
        ('34P_FREIN_SOFT_LIVRE', 'electronique_34p')
    ]},
    'airbag': {'label': 'AIRBAG', 'filter': {'electronique_14m__exact': ''}, 'data': [
        ('14M_RBG_HARD_(AIRBAG)', 'electronique_14m'), ('14M_RBG_SOFT_(AIRBAG)', 'electronique_94m')
    ]},
}

PROD_DICT = {}
for d in [ENGINE_DICT, INTERIOR_DICT, SECURITY_DICT]:
    PROD_DICT.update(d)

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

CAL_DICT = [
    ('OLD', 'electronique_94x'), ('VEHICLE', 'donnee_ligne_de_produit'), ('BRAND', 'donnee_marque_commerciale'),
    ('SILHOUETTE', 'donnee_silhouette'), ('HP', 'attribut_dhb'), ('AMPLI_EQUAL', 'attribut_dun'),
    ('TYPE',  'prods__btel__name')
]


class ExportCorvetIntoExcelTask(ExportExcelTask):
    COL_CORVET = {
        'donnee_marque_commerciale': 'DON_MAR_COMM', 'donnee_silhouette': 'DON_SIL',
        'donnee_genre_de_produit': 'DON_GEN_PROD', 'attribut_dhb': 'ATT_DHB',
        'attribut_dlx': 'ATT_DLX', 'attribut_drc': 'ATT_DRC', 'attribut_dun': 'ATT_DUN',
        'attribut_dym': 'ATT_DYM', 'attribut_dyr': 'ATT_DYR', 'donnee_moteur': 'DON_MOT',
        'donnee_transmission': 'DON_TRA'
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields = []
        self.queryset = None

    def _query_format(self, query):
        data_list = [value for value in query]
        data_list = self.get_vehicle_display(data_list)
        data_list = self.get_multimedia_display(data_list)
        query = self.get_corvet_display(data_list)
        query = tuple([self._timestamp_to_string(_) for _ in query])
        query = tuple([self.noValue if not value else value for value in query])
        return query

    def get_vehicle_display(self, data_list):
        if 'donnee_ligne_de_produit' in self.fields:
            position = self.fields.index('donnee_ligne_de_produit')
            product = data_list[position]
            data = dict(CorvetChoices.vehicles()).get(product, product)
            if 'donnee_marque_commerciale' in self.fields:
                brand = dict(CorvetChoices.brands()).get(data_list[self.fields.index('donnee_marque_commerciale')])
                try:
                    data = literal_eval(data)
                    if brand and isinstance(data, dict):
                        data = data.get(brand)
                except Exception:
                    pass
            data_list[position] = f"{data} | {product}"
        return data_list

    def get_multimedia_display(self, data_list):
        if 'prods__btel__name' in self.fields:
            position = self.fields.index('prods__btel__name')
            data_list[position] = dict(BTEL_PRODUCT_CHOICES).get(data_list[position], data_list[position])
        return data_list

    def get_corvet_display(self, data_list):
        for field, arg in self.COL_CORVET.items():
            if field in self.fields:
                position = self.fields.index(field)
                if data_list[position]:
                    data_list[position] = f"{get_corvet(data_list[position], arg)} | {data_list[position]}"
        return data_list

    def run(self, *args, **kwargs):
        excel_type = kwargs.pop('excel_type', 'xlsx')
        vin_list = kwargs.pop('vin_list', None)
        if vin_list is None:
            if kwargs.get('xelon_model', None):
                filename = f"{kwargs.get('xelon_model')}"
            else:
                filename = f"{kwargs.get('product', 'corvet')}"
            values_list = self.extract_corvet(*args, **kwargs)
        else:
            filename = "ecu"
            values_list = self.extract_ecu(vin_list)
        destination_path = self.file(filename, excel_type, values_list)
        return {
            "detail": "Successfully export CORVET",
            "data": {
                "outfile": destination_path
            }
        }

    def extract_ecu(self, vin_list=None):
        """
        Export ECU data to excel format
        """
        corvets = Corvet.objects.filter(vin__in=vin_list)
        self.header, self.fields = self.get_header_fields(INFO_DICT.get("extract_ecu", []).get('data', []))
        values_list = corvets.values_list(*self.fields).distinct()
        return values_list

    def extract_corvet(self, *args, **kwargs):
        """
        Export CORVET data to excel format
        """
        self._product_filter(**kwargs)
        self._vehicle_filter(**kwargs)
        self._select_columns(**kwargs)
        queryset = self.queryset.annotate(
            date_debut_garantie=Cast(TruncSecond('donnee_date_debut_garantie', DateTimeField()), CharField()))
        if kwargs.get('tag', None):
            queryset = queryset.filter(opts__tag=kwargs.get('tag'))
        if kwargs.get('vins', None):
            vin_list = kwargs.get('vins').split('\r\n')
            queryset = queryset.filter(vin__in=vin_list)
        queryset = self._xelon_filter(queryset, **kwargs)
        if kwargs.get('start_date', None):
            queryset = queryset.filter(donnee_date_debut_garantie__gte=kwargs.get('start_date'))
        if kwargs.get('end_date', None):
            queryset = queryset.filter(donnee_date_debut_garantie__lte=kwargs.get('end_date'))

        values_list = queryset.values_list(*self.fields).distinct()
        return values_list

    def _vehicle_filter(self, **kwargs):
        if kwargs.get('vehicle', None):
            self.queryset = self.queryset.filter(donnee_ligne_de_produit=kwargs.get('vehicle'))
        if kwargs.get('brand', None):
            self.queryset = self.queryset.filter(donnee_marque_commerciale=kwargs.get('brand'))

    def _product_filter(self, **kwargs):
        corvet = Corvet.hw_search(kwargs.get('hw_reference'))
        if PROD_DICT.get(kwargs.get('product')):
            self.queryset = corvet.exclude(**PROD_DICT.get(kwargs.get('product')).get('filter', {}))
        else:
            self.queryset = corvet

    @staticmethod
    def _xelon_filter(queryset, **kwargs):
        if kwargs.get('xelon_vehicle', None):
            queryset = queryset.select_related().filter(xelon__modele_vehicule__startswith=kwargs.get('xelon_vehicle'))
        if kwargs.get('xelon_model', None):
            queryset = queryset.select_related().filter(xelon__modele_produit__startswith=kwargs.get('xelon_model'))
        return queryset

    def _select_columns(self, **kwargs):
        checkbox_dict = {
            'info_cols': INFO_DICT, 'engine_cols': ENGINE_DICT, 'interior_cols': INTERIOR_DICT,
            'security_cols': SECURITY_DICT
        }
        if kwargs.get('product') == "xelon":
            self.header, self.fields = self.get_header_fields(XELON_LIST + DATA_LIST + PRODS_XELON_LIST)
        else:
            data_list = INFO_DICT.get('xelon', []).get('data', []) + INFO_DICT.get('data', []).get('data', [])
            for key, value in checkbox_dict.items():
                for col in kwargs.get(key, []):
                    if isinstance(value, dict):
                        data_list = data_list + value.get(col, []).get('data', [])
                    else:
                        data_list = data_list + value.get(col, [])
            self.header, self.fields = self.get_header_fields(data_list)


class ExportCalIntoExcelTask(ExportCorvetIntoExcelTask):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields = []
        self.queryset = None

    def run(self, *args, **kwargs):
        excel_type = kwargs.pop('excel_type', 'xlsx')
        btel_type = kwargs.pop('btel_type', 'NAC')
        filename = f"CAN_{btel_type}"
        values_list = self.extract(btel_type)
        destination_path = self.file(filename, excel_type, values_list)
        return {
            "detail": "Successfully export CORVET",
            "data": {
                "outfile": destination_path
            }
        }

    def extract(self, btel_type=None):
        """
        Export ECU data to excel format
        """
        queryset = Corvet.objects.exclude(electronique_94x="").order_by('electronique_94x')
        corvets = queryset.filter(prods__btel__name__icontains=btel_type)
        self.header, self.fields = self.get_header_fields(CAL_DICT)
        values_list = corvets.values_list(*self.fields).distinct()
        return values_list
