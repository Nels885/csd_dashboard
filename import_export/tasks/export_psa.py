import re
import os.path
import datetime

from openpyxl import Workbook

from django.db.models.functions import Cast, TruncSecond
from django.db.models import DateTimeField, CharField

from utils.file.export_task import ExportExcelTask
from psa.models import Multimedia
from psa.templatetags.corvet_tags import get_corvet

from psa.models import Corvet


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
    'audio_cfg': [
        ('DHB_HAUT_PARLEUR', 'attribut_dhb'), ('DRC_RECEPTEUR_RADIO', 'attribut_drc'),
        ('DUN_AMPLI_EQUALISEUR', 'attribut_dun'), ('DYR_BTA', 'attribut_dyr')
    ],
    'btel': [
        ('Modele NAV', 'prods__btel__name'), ('14X_BTEL_HARD', 'electronique_14x'),
        ('94X_BTEL_SOFT', 'electronique_94x')
    ],
    'btel_extra': [
        ('44X_BTEL_FOURN.NO.SERIE', 'electronique_44x'), ('64X_BTEL_FOURN.CODE', 'electronique_64x'),
        ('84X_BTEL_DOTE', 'electronique_84x'), ('Réf. Setplate', 'prods__btel__label_ref'),
        ('Niv.', 'prods__btel__level'), ('HW variant', 'prods__btel__extra')
    ],
    'rad': [
        ('Modele RADIO', 'prods__radio__name'), ('14F_RADIO_HARD', 'electronique_14f'),
        ('94F_RADIO_SOFT', 'electronique_94f')
    ],
    'rad_extra': [
        ('44F_RADIO_FOURN.NO.SERIE', 'electronique_44f'), ('64F_RADIO_FOURN.CODE', 'electronique_64f'),
        ('84F_RADIO_DOTE', 'electronique_84f'), ('Réf. Setplate', 'prods__radio__label_ref'),
        ('Niv.', 'prods__radio__level'), ('HW variant', 'prods__radio__extra')
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
        ('94A_CMM_SOFT', 'electronique_94a')
    ],
    'cmm_extra': [
        ('44A_CMM_FOURN.NO.SERIE', 'electronique_44b'),
        ('54A_CMM_FOURN.DATE.FAB', 'electronique_54b'), ('64A_CMM_FOURN.CODE', 'electronique_64b'),
        ('84A_CMM_DOTE', 'electronique_84a'), ('P4A_CMM_EOBD', 'electronique_p4a')
    ],
    'bsi': [
        ('Modèle B.S.I.', 'prods__bsi__name'), ('14B_BSI_HARD', 'electronique_14b'), ('94B_BSI_SOFT', 'electronique_94b')
    ],
    'bsi_extra': [
        ('44B_BSI_FOURN.NO.SERIE', 'electronique_44b'), ('54B_BSI_FOURN.DATE.FAB', 'electronique_54b'),
        ('64B_BSI_FOURN.CODE', 'electronique_64b'), ('84B_BSI_DOTE', 'electronique_84b'), ('HW', 'prods__bsi__hw'),
        ('SW', 'prods__bsi__sw'),
    ],
    'bsm': [
        ('Modele BSM', 'prods__bsm__name'), ('Marque BSM', 'prods__bsm__supplier_oe'),
        ('Ref HW BSM', 'electronique_16b'),
    ],
    'cvm': [
        ('Modèle CVM2', 'prods__cvm2__name'),
        ('12Y_CVM2_2_HARD', 'electronique_12y'), ('92Y_CVM2_2_SOFT', 'electronique_92y')
    ],
    'cvm_extra': [
        ('T2Y_CVM2_2_CODE', 'electronique_t2y'), ('Réf. Setplate CVM2', 'prods__cvm2__label_ref'),
        ('Complément CVM2', 'prods__cvm2__extra')
    ],
    'dae': [
        ('16L_DAE_HARD', 'electronique_16l'),
        ('96L_DAE_SOFT', 'electronique_96l')
    ],
    'abs_esp': [
        ('14P_FREIN_HARD', 'electronique_14p'), ('94P_FREIN_SOFT', 'electronique_94p'),
        ('34P_FREIN_SOFT_LIVRE', 'electronique_34p')
    ],
    'airbag': [
        ('14M_RBG_HARD_(AIRBAG)', 'electronique_14m'), ('14M_RBG_SOFT_(AIRBAG)', 'electronique_94m')
    ],
    'extra_ecu': [
        ('Numero de dossier', 'xelon__numero_de_dossier'), ('V.I.N.', 'vin'),
        ('Modele produit', 'xelon__modele_produit'), ('Modele vehicule', 'xelon__modele_vehicule'),
        ('DATE_DEBUT_GARANTIE', 'donnee_date_debut_garantie'), ('14A_CMM_HARD', 'electronique_14a'),
        ('34A_CMM_SOFT_LIVRE', 'electronique_34a'), ('94A_CMM_SOFT', 'electronique_94a'),
        ('44A_CMM_FOURN.NO.SERIE', 'electronique_44a'), ('54A_CMM_FOURN.DATE.FAB', 'electronique_54a'),
        ('64A_CMM_FOURN.CODE', 'electronique_64a'), ('84A_CMM_DOTE', 'electronique_84a'),
        ('P4A_CMM_EOBD', 'electronique_p4a')
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


class ExportCorvetIntoExcelTask(ExportExcelTask):
    COL_CORVET = {
        'donnee_ligne_de_produit': 'DON_LIN_PROD', 'donnee_silhouette': 'DON_SIL',
        'donnee_genre_de_produit': 'DON_GEN_PROD', 'attribut_dhb': 'ATT_DHB',
        'attribut_dlx': 'ATT_DLX', 'attribut_drc': 'ATT_DRC', 'attribut_dun': 'ATT_DUN',
        'attribut_dym': 'ATT_DYM', 'attribut_dyr': 'ATT_DYR', 'donnee_moteur': 'DON_MOT'
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _query_format(self, query):
        data_list = [value for value in query]
        data_list = self.get_multimedia_display(data_list)
        query = self.get_corvet_display(data_list)
        query = tuple([_.strftime("%d/%m/%Y %H:%M:%S") if isinstance(_, datetime.date) else _ for _ in query])
        query = tuple([self.noValue if not value else value for value in query])
        return query

    def get_multimedia_display(self, data_list):
        if 'prods__btel__name' in self.fields:
            position = self.fields.index('prods__btel__name')
            for prod in Multimedia.PRODUCT_CHOICES:
                if prod[0] == data_list[position]:
                    data_list[position] = prod[1]
                    break
        return data_list

    def get_corvet_display(self, data_list):
        for field, arg in self.COL_CORVET.items():
            if field in self.fields:
                position = self.fields.index(field)
                if data_list[position]:
                    if 'vin' in self.fields and arg == 'DON_LIN_PROD':
                        if re.match(r'^[V][FR]7\w{14}$', str(data_list[self.fields.index('vin')])):
                            arg = 'DON_LIN_PROD 1'
                        else:
                            arg = 'DON_LIN_PROD 0'
                    data_list[position] = f"{get_corvet(data_list[position], arg)} | {data_list[position]}"
        return data_list

    def run(self, *args, **kwargs):
        path = self.copy_and_get_copied_path()
        excel_type = kwargs.pop('excel_type', 'xlsx')
        vin_list = kwargs.pop('vin_list', None)
        if vin_list is None:
            if kwargs.get('xelon_model', None):
                filename = f"{kwargs.get('xelon_model')}_{self.date.strftime('%y-%m-%d_%H-%M')}"
            else:
                filename = f"{kwargs.get('product', 'corvet')}_{self.date.strftime('%y-%m-%d_%H-%M')}"
            values_list = self.extract_corvet(*args, **kwargs)
        else:
            filename = f"ecu_{self.date.strftime('%y-%m-%d_%H-%M')}"
            values_list = self.extract_ecu(vin_list)
        destination_path = os.path.join(path, f"{filename}.{excel_type}")
        workbook = Workbook()
        workbook = self.create_workbook(workbook, self.header, values_list)
        workbook.save(filename=destination_path)
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
        self.header, self.fields = self.get_header_fields(CORVET_DICT.get("extract_ecu", []))
        values_list = corvets.values_list(*self.fields).distinct()
        return values_list

    def extract_corvet(self, *args, **kwargs):
        """
        Export CORVET data to excel format
        """
        prod_dict = {
            'btel': {'electronique_14x__exact': ''}, 'rad': {'electronique_14f__exact': ''},
            'ecu': {'electronique_14a__exact': ''}, 'bsi': {'electronique_14b__exact': ''},
            'com200x': {'electronique_16p__exact': ''}, 'bsm': {'electronique_16p__exact': ''},
            'cvm': {'electronique_12y__exact': ''}, 'dae': {'electronique_16l__exact': ''},
            'abs_esp': {'electronique_14p__exact': ''}, 'airbag': {'electronique_14m__exact': ''},
            'emf': {'electronique_16l__exact': ''}, 'cmb': {'electronique_14k__exact': ''}
        }
        product = kwargs.get('product', 'bsi')
        data_list = CORVET_DICT['xelon'] + CORVET_DICT['data']
        for col in kwargs.get('columns', []):
            data_list.extend(CORVET_DICT.get(col, []))
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
        self.header, self.fields = self.get_header_fields(data_list)
        if prod_dict.get(product):
            queryset = queryset.exclude(**prod_dict.get(product))
        elif product == "xelon":
            self.header, self.fields = self.get_header_fields(XELON_LIST + DATA_LIST + PRODS_XELON_LIST)
        values_list = queryset.values_list(*self.fields).distinct()[:30000]
        return values_list
