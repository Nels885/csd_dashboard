import re
from ast import literal_eval

from django.db import models, utils
from django.db.models import Q

from .choices import BTEL_PRODUCT_CHOICES, BTEL_TYPE_CHOICES, ECU_TYPE_CHOICES, CAL_TYPE_CHOICES

CORVET_LIST = [
    ('electronique_14a', 'electronique_94a', 'electronique_34a'), ('electronique_14b', 'electronique_94b'),
    ('electronique_16b', 'electronique_96b'), ('electronique_14d', 'electronique_94d'),
    ('electronique_12e', 'electronique_92e'), ('electronique_14f', 'electronique_94f'),
    ('electronique_16g', 'electronique_96g'), ('electronique_14j', 'electronique_94j'),
    ('electronique_14k', 'electronique_94k'), ('electronique_14l', 'electronique_94l'),
    ('electronique_16l', 'electronique_96l'), ('electronique_11m',), ('electronique_14m', 'electronique_94m'),
    ('electronique_11n',), ('electronique_14p', 'electronique_94p', 'electronique_34p'), ('electronique_16p',),
    ('electronique_11q', 'electronique_91q'), ('electronique_16q', 'electronique_96q'),
    ('electronique_14r', 'electronique_94r', 'electronique_34r'), ('electronique_19u',), ('electronique_16v',),
    ('electronique_19v',), ('electronique_19w',), ('electronique_14x', 'electronique_94x'),
    ('electronique_12y', 'electronique_92y'), ('electronique_14y',)
]

CORVET_FILTERS = [
    'vin__iexact', 'vin__iendswith', 'opts__tag__istartswith'
]

CORVET_SN_FILTERS = [
    'electronique_44l__icontains', 'electronique_44x__icontains','electronique_44a__icontains',
    'electronique_44b__iexact', 'electronique_46p__iexact'
]

CORVET_HW_FILTERS = [f'{value}__iexact' for value in [
    'electronique_14f', 'electronique_14j', 'electronique_14k', 'electronique_14l', 'electronique_14r',
    'electronique_14x', 'prods__btel__label_ref', 'electronique_19z', 'electronique_19h', 'electronique_14a',
    'electronique_14b', 'electronique_16p', 'electronique_16b', 'electronique_16q', 'electronique_16v',
    'electronique_19f', 'electronique_19u', 'electronique_14d', 'electronique_16g', 'electronique_19v',
    'electronique_12y', 'prods__cvm2__label_ref',
    'electronique_16l', 'electronique_14y', 'electronique_14z', 'electronique_14p', 'electronique_19w',
    'electronique_16t', 'electronique_19t', 'electronique_14m', 'electronique_18z', 'electronique_11m',
    'electronique_19k', 'electronique_12e', 'electronique_11q', 'electronique_11n', 'electronique_1m2',
    'electronique_1l9'
]]

CORVET_SW_FILTERS = [f'{value}__iexact' for value in [
    'electronique_94f', 'electronique_94j', 'electronique_94l', 'electronique_94x', 'electronique_99h',
    'electronique_34a', 'electronique_94a', 'electronique_94b', 'electronique_96b', 'electronique_94r',
    'electronique_96q', 'electronique_94d', 'electronique_96g', 'electronique_94j', 'electronique_94k',
    'electronique_92y', 'electronique_96l', 'electronique_94p', 'electronique_34p', 'electronique_94m',
    'electronique_99k', 'electronique_92e', 'electronique_91q', 'electronique_34r'
]]


class CorvetChoices(models.Model):
    COL_CHOICES = [
        ('DON_LIN_PROD', 'donnee_ligne_de_produit'), ('DON_MAR_COMM', 'donnee_marque_commerciale'),
        ('DON_SIL', 'donnee_silhouette'), ('DON_GEN_PROD', 'donnee_genre_de_produit'), ('DON_MOT', 'MOTEUR'),
        ('DON_TRA', 'TRANSMISSION'),

        ('ATT_D5J', 'VERSIONS RADIO'), ('ATT_DAO', 'SURVEILLANCE VOIE LATERALE'), ('ATT_DAZ', 'ALIMENTATION'),
        ('ATT_DCP', 'GRADUATION VITESSES'), ('ATT_DDC', 'DEPOLLUTION (MOTEUR)'),
        ('ATT_DHB', 'HAUT PARLEUR'), ('ATT_DHG', 'COMMANDE AUTO-RADIO'), ('ATT_DJY', 'SYSTEME NAVIGATION'),
        ('ATT_DLX', 'AFFICHEUR AV'), ('ATT_DUN', 'AMPLI EQUALISEUR'), ('ATT_DYM', 'PRISE AUXILIAIRE PACK AUDIO'),
        ('ATT_DYR', 'BOITIER TELEMATIQUE'), ('ATT_DAT', 'ANTENNE'), ('ATT_DCD', 'CARBURANT (RON MINI MOTEUR)'),
        ('ATT_DCX', 'COTE CONDUITE/POSTE CONDUITE'), ('ATT_DE2', 'MIRROR LINK'), ('ATT_DE3', 'RECHARGE NOMADE'),
        ('ATT_DE4', 'JUKE BOX'), ('ATT_DE7', 'AFFICHAGE PANNEAU ROUTIER'), ('ATT_DES', 'PRISE ACCESSOIRES'),
        ('ATT_DGM', 'COMBINE (CARACTERISTIQUES)'), ('ATT_DI2', 'RECONNAISSANCE VOCALE'),
        ('ATT_DJZ', 'FREQUENCE TELECDE CONDAMNATION'), ('ATT_DN1', 'NIGHT VISION'),
        ('ATT_DPR', 'PROJECTEUR ANTI-BROUILLARD'), ('ATT_DQK', 'AIDE VISUELLE PANORAMIQUE'),
        ('ATT_DQP', 'AFFICHAGE COMPL DETECTION EXT'), ('ATT_DRC', 'RECEPTEUR RADIO'),
        ('ATT_DSB', 'SURVEILLANCE / LIMITATION VIT'), ('ATT_DTI', 'TUNER-RADIO'), ('ATT_DUB', 'DETECTION OBSTACLE'),
        ('ATT_DUE', 'DETECTION SOUS GONFLAGE'), ('ATT_DUF', 'SYSTEME ESP/ESC'), ('ATT_DUO', 'AFFICHEUR COMPLEMENTAIRE'),
        ('ATT_DUZ', 'FREQUENCE RADIO'), ('ATT_DYC', 'STOP AND START'), ('ATT_DYQ', 'ALLUMAGE FEUX'),
        ('ATT_DZE', 'PACK VISION'),

        ('ELE_14R', 'AAS HARD - Aide Au Stationnement')
    ]

    key = models.CharField('clé', max_length=10)
    value = models.CharField('valeur', max_length=200)
    column = models.CharField('colonne', max_length=100, choices=COL_CHOICES)

    class Meta:
        verbose_name = "Convertion données CORVET"
        ordering = ['pk']
        constraints = [
            models.UniqueConstraint(fields=['key', 'column'], name='key_column_unique')
        ]

    @classmethod
    def brands(cls):
        try:
            return [('', '---')] + list(cls.objects.filter(column='DON_MAR_COMM').values_list('key', 'value'))
        except utils.ProgrammingError:
            return []

    @classmethod
    def vehicles(cls, form=False):
        try:
            if form:
                data = [('', '---')]
                for key, value in list(cls.objects.filter(column='DON_LIN_PROD').values_list('key', 'value')):
                    try:
                        value_dict = literal_eval(value)
                        if isinstance(value_dict, dict):
                            value = ' | '.join([value for value in value_dict.values()])
                    except Exception:
                        pass
                    data.append((key, value))
                return data
            return [('', '---')] + list(cls.objects.filter(column='DON_LIN_PROD').values_list('key', 'value'))
        except utils.ProgrammingError:
            return []

    def __str__(self):
        return f"{self.key} - {self.value} - {self.column}"


class Corvet(models.Model):
    vin = models.CharField('V.I.N.', max_length=17, primary_key=True)
    donnee_date_debut_garantie = models.DateTimeField('Date début garantie', null=True, blank=True)
    donnee_date_entree_montage = models.DateTimeField('Date entrée montage', null=True, blank=True)
    donnee_ligne_de_produit = models.CharField('LIGNE_DE_PRODUIT', max_length=200, blank=True)
    donnee_marque_commerciale = models.CharField('MARQUE_COMMERCIALE', max_length=200, blank=True)
    donnee_silhouette = models.CharField('SILHOUETTE', max_length=200, blank=True)
    donnee_genre_de_produit = models.CharField('GENRE_DE_PRODUIT', max_length=200, blank=True)
    attribut_ddo = models.CharField('KIT TELEPHONE MAIN LIBRE', max_length=200, blank=True)
    attribut_dgm = models.CharField('COMBINE (CARACTERISTIQUES)', max_length=200, blank=True)
    attribut_dhb = models.CharField('HAUT PARLEUR', max_length=200, blank=True)
    attribut_dhg = models.CharField('COMMANDE AUTO-RADIO', max_length=200, blank=True)
    attribut_djq = models.CharField('COMPACT DISQUE', max_length=200, blank=True)
    attribut_djy = models.CharField('SYSTEME NAVIGATION', max_length=200, blank=True)
    attribut_dkx = models.CharField('CARTOGRAPHIE POUR NAVIGATION', max_length=200, blank=True)
    attribut_dlx = models.CharField('AFFICHEUR AV', max_length=200, blank=True)
    attribut_doi = models.CharField('RECEPTION RADIO AMELIOREE', max_length=200, blank=True)
    attribut_dqm = models.CharField('TYPAGE GMP', max_length=200, blank=True)
    attribut_dqs = models.CharField('WIFI', max_length=200, blank=True)
    attribut_drc = models.CharField('RECEPTEUR RADIO', max_length=200, blank=True)
    attribut_drt = models.CharField('REGULATION CLIMAT/TEMPERATURE', max_length=200, blank=True)
    attribut_dti = models.CharField('TUNER RADIO', max_length=200, blank=True)
    attribut_dun = models.CharField('AMPLI EQUALISEUR', max_length=200, blank=True)
    attribut_dwl = models.CharField('PACK RADIO/INFO/COMMUNICATION', max_length=200, blank=True)
    attribut_dwt = models.CharField('PACK PREEQUIP. RADIO/COMMUNIC.', max_length=200, blank=True)
    attribut_dxj = models.CharField('ECRAN VIDEO AR', max_length=200, blank=True)
    attribut_dyb = models.CharField('VISION TETE HAUTE', max_length=200, blank=True)
    attribut_dym = models.CharField('PRISE AUXILIAIRE PACK AUDIO', max_length=200, blank=True)
    attribut_dyr = models.CharField('BOITIER TELEMATIQUE', max_length=200, blank=True)
    attribut_dzv = models.CharField('AIDE A LA CONDUITE', max_length=200, blank=True)
    attribut_gg8 = models.CharField('PAYS PROGRAMME (ICP)', max_length=200, blank=True)
    electronique_14f = models.CharField('RADIO HARD - Recepteur Radio', max_length=200, blank=True)
    electronique_14j = models.CharField('CLIM HARD - Climatisation', max_length=200, blank=True)
    electronique_14k = models.CharField('CMB HARD - Combine Planche de Bord', max_length=200, blank=True)
    electronique_14l = models.CharField('EMF HARD - Ecran Multifonctions', max_length=200, blank=True)
    electronique_14r = models.CharField('AAS HARD - Aide Au Stationnement', max_length=200, blank=True)
    electronique_14x = models.CharField('BTEL HARD - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    electronique_19z = models.CharField('FMUX_HARD - FAÇADE MULTIPLEXÉ', max_length=200, blank=True)
    electronique_44f = models.CharField('RADIO FOURN.NO.SERIE - Recepteur Radio', max_length=200, blank=True)
    electronique_44l = models.CharField('EMF FOURN.NO.SERIE - Ecran Multifonctions', max_length=200, blank=True)
    electronique_44x = models.CharField('BTEL FOURN.NO.SERIE - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    electronique_54f = models.CharField('RADIO FOURN.DATE.FAB - Recepteur Radio', max_length=200, blank=True)
    electronique_54k = models.CharField('CMB FOURN.DATE.FAB - Combine Planche de Bord', max_length=200, blank=True)
    electronique_54l = models.CharField('EMF FOURN.DATE.FAB - Ecran Multifonctions', max_length=200, blank=True)
    electronique_84f = models.CharField('RADIO DOTE - Recepteur Radio', max_length=200, blank=True)
    electronique_84l = models.CharField('EMF DOTE - Ecran Multifonctions', max_length=200, blank=True)
    electronique_84x = models.CharField('BTEL DOTE - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    electronique_94f = models.CharField('RADIO SOFT - Recepteur Radio', max_length=200, blank=True)
    electronique_94l = models.CharField('EMF SOFT - Ecran Multifonctions', max_length=200, blank=True)
    electronique_94x = models.CharField('BTEL SOFT - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    attribut_dat = models.CharField('ANTENNE', max_length=200, blank=True)
    attribut_dcx = models.CharField('COTE CONDUITE/POSTE CONDUITE', max_length=200, blank=True)
    electronique_19h = models.CharField('MDS HARD - Module de service telematique', max_length=200, blank=True)
    electronique_49h = models.CharField('MDS FOURN.NO.SERIE - Module de service telematique', max_length=200, blank=True)
    electronique_64f = models.CharField('RADIO FOURN.CODE - Recepteur Radio', max_length=200, blank=True)
    electronique_64x = models.CharField('BTEL FOURN.CODE - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    electronique_69h = models.CharField('MDS FOURN.CODE - Module de service telematique', max_length=200, blank=True)
    electronique_89h = models.CharField('MDS DOTE - Module de service telematique', max_length=200, blank=True)
    electronique_99h = models.CharField('MDS SOFT - Module de service telematique', max_length=200, blank=True)
    electronique_14a = models.CharField('CMM HARD - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_34a = models.CharField('CMM SOFT LIVRE - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_44a = models.CharField('CMM FOURN.NO.SERIE - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_54a = models.CharField('CMM FOURN.DATE.FAB - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_64a = models.CharField('CMM FOURN.CODE - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_84a = models.CharField('CMM DOTE - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_94a = models.CharField('CMM SOFT - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_p4a = models.CharField('CMM EOBD - Calculateur Moteur Multifonction', max_length=200, blank=True)
    donnee_moteur = models.CharField('MOTEUR', max_length=200, blank=True)
    donnee_transmission = models.CharField('TRANSMISSION', max_length=200, blank=True)
    organes_10 = models.CharField('MOTEUR', max_length=200, blank=True)
    electronique_14b = models.CharField('BSI HARD - Boitier Servitude Intelligent', max_length=200, blank=True)
    organes_20 = models.CharField('BOITE DE VITESSES', max_length=200, blank=True)
    electronique_44b = models.CharField('BSI FOURN.NO.SERIE - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_54b = models.CharField('BSI FOURN.DATE.FAB - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_64b = models.CharField('BSI FOURN.CODE - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_84b = models.CharField('BSI DOTE - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_94b = models.CharField('BSI SOFT - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_16p = models.CharField('HDC HARD - Haut de Colonne de Direction (COM200x)', max_length=200, blank=True)
    electronique_46p = models.CharField('HDC FOURN.NO.SERIE - Haut de Colonne de Direction (COM200x)', max_length=200, blank=True)
    electronique_56p = models.CharField('HDC FOURN.DATE.FAB - Haut de Colonne de Direction (COM200x)', max_length=200, blank=True)
    electronique_66p = models.CharField('HDC FOURN.CODE - Haut de Colonne de Direction (COM200x)', max_length=200, blank=True)
    electronique_16b = models.CharField('BSM HARD - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_46b = models.CharField('BSM FOURN.NO.SERIE - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_56b = models.CharField('BSM FOURN.DATE.FAB - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_66b = models.CharField('BSM FOURN.CODE - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_86b = models.CharField('BSM DOTE - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_96b = models.CharField('BSM SOFT - Boitier Servitude Moteur', max_length=200, blank=True)

    attribut_dao = models.CharField('SURVEILLANCE VOIE LATERALE', max_length=200, blank=True)
    attribut_dcd = models.CharField('CARBURANT (RON MINI MOTEUR)', max_length=200, blank=True)
    attribut_de2 = models.CharField('MIRROR LINK', max_length=200, blank=True)
    attribut_de3 = models.CharField('RECHARGE NOMADE', max_length=200, blank=True)
    attribut_de4 = models.CharField('JUKE BOX', max_length=200, blank=True)
    attribut_dpr = models.CharField('PROJECTEUR ANTI-BROUILLARD', max_length=200, blank=True)
    attribut_dqk = models.CharField('AIDE VISUELLE PANORAMIQUE', max_length=200, blank=True)
    attribut_dqp = models.CharField('AFFICHAGE COMPL DETECTION EXT', max_length=200, blank=True)
    attribut_dub = models.CharField('DETECTION OBSTACLE', max_length=200, blank=True)
    attribut_due = models.CharField('DETECTION SOUS GONFLAGE', max_length=200, blank=True)
    attribut_duf = models.CharField('SYSTEME ESP/ESC', max_length=200, blank=True)
    attribut_dyc = models.CharField('STOP AND START', max_length=200, blank=True)
    attribut_dyq = models.CharField('ALLUMAGE FEUX', max_length=200, blank=True)
    attribut_dze = models.CharField('PACK VISION', max_length=200, blank=True)
    electronique_94r = models.CharField('AAS SOFT - Aide Au Stationnement', max_length=200, blank=True)
    electronique_16q = models.CharField('BCM HARD - Boitier coffre Motorise', max_length=200, blank=True)
    electronique_96q = models.CharField('BCM SOFT - Boitier coffre Motorise', max_length=200, blank=True)
    electronique_16v = models.CharField('BCPM HARD - Projecteur gauche avec fonctionnalites de correction integrees', max_length=200, blank=True)
    electronique_19f = models.CharField('BECB HARD - Boitier Electronique Etat charge Batterie', max_length=200, blank=True)
    electronique_19u = models.CharField('BEM HARD - Boitier Eclairage Memorisation', max_length=200, blank=True)
    electronique_14d = models.CharField('BV HARD - Boite Vitesses', max_length=200, blank=True)
    electronique_94d = models.CharField('BV SOFT - Boite Vitesses', max_length=200, blank=True)
    electronique_16g = models.CharField('CDPL HARD - Capteur de pluie/luminosite', max_length=200, blank=True)
    electronique_96g = models.CharField('CDPL SOFT - Capteur de pluie/luminosite', max_length=200, blank=True)
    electronique_94j = models.CharField('CLIM SOFT - Climatisation', max_length=200, blank=True)
    electronique_94k = models.CharField('CMB SOFT - Combine Planche de Bord', max_length=200, blank=True)
    electronique_19v = models.CharField('CRT HARD - Leve Vitre Arriere Droit', max_length=200, blank=True)
    electronique_12y = models.CharField('CVM2_2_ HARD - CAMERA VIDEO MULTIFONCTION V2', max_length=200, blank=True)
    electronique_92y = models.CharField('CVM2_2_ SOFT - CAMERA VIDEO MULTIFONCTION V2', max_length=200, blank=True)
    electronique_16l = models.CharField('DAE HARD - Direction Assistee Electrique', max_length=200, blank=True)
    electronique_96l = models.CharField('DAE SOFT - Direction Assistee Electrique', max_length=200, blank=True)
    electronique_14y = models.CharField('EDP HARD - Electronique De Porte Conducteur', max_length=200, blank=True)
    electronique_14z = models.CharField('EDP_P HARD - Electronique De Porte Passager', max_length=200, blank=True)
    electronique_14p = models.CharField('FREIN HARD - Frein ABS/ESP/EHB Frein Principal', max_length=200, blank=True)
    electronique_94p = models.CharField('FREIN SOFT - Frein ABS/ESP/EHB Frein Principal', max_length=200, blank=True)
    electronique_34p = models.CharField('FREIN SOFT LIVRE - Frein ABS/ESP/EHB Frein Principal', max_length=200, blank=True)
    electronique_19w = models.CharField('LVARG HARD - Leve Vitre Arriere Gauche', max_length=200, blank=True)
    electronique_16t = models.CharField('MOTEV HARD - Moteur Essuie-Vitre', max_length=200, blank=True)
    electronique_19t = models.CharField('PDPC HARD - Platine de Porte Conducteur', max_length=200, blank=True)
    electronique_14m = models.CharField('RBG HARD - Boitier Air Bag (Sac Gonflable)', max_length=200, blank=True)
    electronique_94m = models.CharField('RBG SOFT - Boitier Air Bag (Sac Gonflable)', max_length=200, blank=True)
    electronique_18z = models.CharField('TNB HARD - Boitier de non Bouclage Ceinture Securite', max_length=200, blank=True)
    electronique_11m = models.CharField('VMF HARD - MODULE COMMUTATION INTEGRE', max_length=200, blank=True)

    # Adding the 22/11/2021
    electronique_19k = models.CharField('ARTIV HARD - Boitier Aide au Respect du Temps Inter Vehicule', max_length=200, blank=True)
    electronique_49k = models.CharField('ARTIV FOURN.NO.SERIE - Boitier Aide au Respect du Temps Inter Vehicule', max_length=200, blank=True)
    electronique_59k = models.CharField('ARTIV FOURN.DATE.FAB - Boitier Aide au Respect du Temps Inter Vehicule', max_length=200, blank=True)
    electronique_69k = models.CharField('ARTIV FOURN.CODE - Boitier Aide au Respect du Temps Inter Vehicule', max_length=200, blank=True)
    electronique_99k = models.CharField('ARTIV SOFT - Boitier Aide au Respect du Temps Inter Vehicule', max_length=200, blank=True)
    electronique_12e = models.CharField('AVM - HARD - AIDE VISUELLE A LA MANOEUVRE', max_length=200, blank=True)
    electronique_42e = models.CharField('AVM - FNR NO SERIE - AIDE VISUELLE A LA MANŒUVRE', max_length=200, blank=True)
    electronique_52e = models.CharField('AVM - FNR DATE - AIDE VISUELLE A LA MANŒUVRE', max_length=200, blank=True)
    electronique_62e = models.CharField('AVM - FNR CODE - AIDE VISUELLE A LA MANŒUVRE', max_length=200, blank=True)
    electronique_92e = models.CharField('AVM - SOFT - AIDE VISUELLE A LA MANŒUVRE', max_length=200, blank=True)
    electronique_k9h = models.CharField('BTA - NUMERO IMEI: INTERNATIONAL MOBILE EQUIPMENT IDENTITY', max_length=200, blank=True)
    electronique_m9h = models.CharField('BTA - NUMERO IMSI: INTERNATIONAL MOBILE SUBSCRIBER IDENTITY', max_length=200, blank=True)
    electronique_r9h = models.CharField('BTA - NUMERO ICCID: INTEGRATED CICUIT CARD ID', max_length=200, blank=True)
    electronique_t2y = models.CharField('CVM2_2_CODE CAMERA VIDEO MULTIFONCTION V2', max_length=200, blank=True)
    attribut_d5j = models.CharField('VERSIONS RADIO', max_length=200, blank=True)
    attribut_daz = models.CharField('ALIMENTATION', max_length=200, blank=True)
    attribut_dcp = models.CharField('GRADUATION VITESSES', max_length=200, blank=True)
    attribut_ddc = models.CharField('DEPOLLUTION (MOTEUR)', max_length=200, blank=True)
    attribut_de7 = models.CharField('AFFICHAGE PANNEAU ROUTIER', max_length=200, blank=True)
    attribut_de8 = models.CharField('ALERTE VIGILANCE CONDUCTEUR', max_length=200, blank=True)
    attribut_des = models.CharField('PRISE ACCESSOIRES', max_length=200, blank=True)
    attribut_di2 = models.CharField('RECONNAISSANCE VOCALE', max_length=200, blank=True)
    attribut_djz = models.CharField('FREQUENCE TELECDE CONDAMNATION', max_length=200, blank=True)
    attribut_dn1 = models.CharField('NIGHT VISION', max_length=200, blank=True)
    attribut_dsb = models.CharField('SURVEILLANCE / LIMITATION VIT', max_length=200, blank=True)
    attribut_duo = models.CharField('AFFICHEUR COMPLEMENTAIRE', max_length=200, blank=True)
    attribut_duz = models.CharField('FREQUENCE RADIO', max_length=200, blank=True)

    # Adding the 22/11/2021
    electronique_11q = models.CharField('DMTX_HARD - DISPOSITIF MAINTIEN TENSION', max_length=200, blank=True)
    electronique_41q = models.CharField('DMTX_FOURN.NO.SERIE - DISPOSITIF MAINTIEN TENSION', max_length=200, blank=True)
    electronique_51q = models.CharField('DMTX_FOURN.DATE.FAB - DISPOSITIF MAINTIEN TENSION', max_length=200, blank=True)
    electronique_61q = models.CharField('DMTX_FOURN.CODE - DISPOSITIF MAINTIEN TENSION', max_length=200, blank=True)
    electronique_91q = models.CharField('DMTX_SOFT - DISPOSITIF MAINTIEN TENSION', max_length=200, blank=True)
    electronique_14e = models.CharField('HARD - NAVIGATION Abandonne', max_length=200, blank=True)
    electronique_1f4 = models.CharField('SDCM_HARD - BOITIER DE GESTION DES COMMUNICATIONS A COURTES DISTANCES', max_length=200, blank=True)
    electronique_1j6 = models.CharField('HARD - DETECTION PRESENCE DES MAINS SUR LE VOLANT', max_length=200, blank=True)
    electronique_1j8 = models.CharField('CAMERA FRONTALE MULTIFONCTIONS', max_length=200, blank=True)
    electronique_1j9 = models.CharField('HARD - FRONT RADAR', max_length=200, blank=True)
    electronique_1k4 = models.CharField('VSM_HARD - MODULE SUPERVISION VEHICULE', max_length=200, blank=True)
    electronique_1k5 = models.CharField('HARD - VEHICLE COMPARTMENT CONTROL UNIT', max_length=200, blank=True)
    electronique_1k9 = models.CharField('HARD - RECONFIGURABLE TOUCH SCREEN', max_length=200, blank=True)
    electronique_1l9 = models.CharField('BOITIER SERVITUDE RADIO FREQUENCE', max_length=200, blank=True)
    electronique_1m2 = models.CharField('IN-VEHICULE INFOTAINMENT', max_length=200, blank=True)
    electronique_34r = models.CharField('AAS SOFT LIVRE - Aide Au Stationnement', max_length=200, blank=True)
    electronique_3f4 = models.CharField('SDCM_SOFT.LIVRE - BOITIER DE GESTION DES COMMUNICATIONS A COURTES DISTANCES', max_length=200, blank=True)
    electronique_3j8 = models.CharField('CAMERA FRONTALE MULTIFONCTIONS', max_length=200, blank=True)
    electronique_3j9 = models.CharField('DELIVERED SOFT. - FRONT RADAR', max_length=200, blank=True)
    electronique_3k5 = models.CharField('DELIVERED SOFT. - VEHICLE COMPARTMENT CONTROL UNIT', max_length=200, blank=True)
    electronique_3l9 = models.CharField('BOITIER SERVITUDE RADIO FREQUENCE', max_length=200, blank=True)
    electronique_3m2 = models.CharField('IN-VEHICULE INFOTAINMENT', max_length=200, blank=True)
    electronique_44e = models.CharField('FOURN.NO.SERIE - NAVIGATION Abandonne', max_length=200, blank=True)
    electronique_4j8 = models.CharField('CAMERA FRONTALE MULTIFONCTIONS', max_length=200, blank=True)
    electronique_4l9 = models.CharField('BOITIER SERVITUDE RADIO FREQUENCE', max_length=200, blank=True)
    electronique_4m2 = models.CharField('IN-VEHICULE INFOTAINMENT', max_length=200, blank=True)
    electronique_54e = models.CharField('FOURN.DATE.FAB - NAVIGATION Abandonne', max_length=200, blank=True)
    electronique_5j6 = models.CharField('FOURN.DATE.FAB - DETECTION PRESENCE DES MAINS SUR LE VOLANT', max_length=200, blank=True)
    electronique_5j8 = models.CharField('CAMERA FRONTALE MULTIFONCTIONS', max_length=200, blank=True)
    electronique_5j9 = models.CharField('SUPPLIER DATE - FRONT RADAR', max_length=200, blank=True)
    electronique_5m2 = models.CharField('IN-VEHICULE INFOTAINMENT', max_length=200, blank=True)
    electronique_64e = models.CharField('FOURN.CODE - NAVIGATION Abandonne', max_length=200, blank=True)
    electronique_6j6 = models.CharField('FOURN.CODE - DETECTION PRESENCE DES MAINS SUR LE VOLANT', max_length=200, blank=True)
    electronique_6j8 = models.CharField('CAMERA FRONTALE MULTIFONCTIONS', max_length=200, blank=True)
    electronique_6j9 = models.CharField('SUPPLIER CODE - FRONT RADAR', max_length=200, blank=True)
    electronique_6k4 = models.CharField('VSM_FOURN.CODE - MODULE SUPERVISION VEHICULE', max_length=200, blank=True)
    electronique_6k5 = models.CharField('SUPPLIER CODE - VEHICLE COMPARTMENT CONTROL UNIT', max_length=200, blank=True)
    electronique_6k9 = models.CharField('SUPPLIER CODE - RECONFIGURABLE TOUCH SCREEN', max_length=200, blank=True)
    electronique_6l9 = models.CharField('BOITIER SERVITUDE RADIO FREQUENCE', max_length=200, blank=True)
    electronique_6m2 = models.CharField('IN-VEHICULE INFOTAINMENT', max_length=200, blank=True)
    electronique_8j8 = models.CharField('CAMERA FRONTALE MULTIFONCTIONS', max_length=200, blank=True)
    electronique_8j9 = models.CharField('DOTE - FRONT RADAR', max_length=200, blank=True)
    electronique_8k4 = models.CharField('VSM_DOTE - MODULE SUPERVISION VEHICULE', max_length=200, blank=True)
    electronique_8l9 = models.CharField('BOITIER SERVITUDE RADIO FREQUENCE', max_length=200, blank=True)
    electronique_8m2 = models.CharField('IN-VEHICULE INFOTAINMENT', max_length=200, blank=True)
    electronique_9f4 = models.CharField('SDCM_SOFT - BOITIER DE GESTION DES COMMUNICATIONS A COURTES DISTANCES', max_length=200, blank=True)
    electronique_9j8 = models.CharField('CAMERA FRONTALE MULTIFONCTIONS', max_length=200, blank=True)
    electronique_9j9 = models.CharField('SOFT. - FRONT RADAR', max_length=200, blank=True)
    electronique_9k4 = models.CharField('VSM_SOFT - MODULE SUPERVISION VEHICULE', max_length=200, blank=True)
    electronique_9k5 = models.CharField('SOFT. - VEHICLE COMPARTMENT CONTROL UNIT', max_length=200, blank=True)
    electronique_9l9 = models.CharField('BOITIER SERVITUDE RADIO FREQUENCE', max_length=200, blank=True)
    electronique_kl9 = models.CharField('BSRF - NUMERO IMEI: INTERNATIONAL MOBILE EQUIPMENT IDENTITY', max_length=200, blank=True)
    electronique_ml9 = models.CharField('BSRF - NUMERO IMSI: INTERNATIONAL MOBILE SUBSCRIBER IDENTITY', max_length=200, blank=True)
    electronique_p4d = models.CharField('BVA EOBD - Boitier Arret et Démarrage Moteur (STOP & START)', max_length=200, blank=True)
    electronique_rl9 = models.CharField('BSRF - NUMERO ICCID: INTEGRATED CICUIT CARD ID', max_length=200, blank=True)
    electronique_tj8 = models.CharField('FRONT CAMERA PARAMETRES D APPRENTISSAGE', max_length=200, blank=True)
    electronique_vj8 = models.CharField('FRONT CAMERA HAUTEUR SOUS BERCEAU', max_length=200, blank=True)
    electronique_xm2 = models.CharField('DATA LIBRARY - IVI - IN-VEHICULE INFOTAINMENT', max_length=200, blank=True)
    electronique_yl9 = models.CharField('VEHICLE APP - BSRF - BOITIER SERVITUDE RADIO FREQUENCE', max_length=200, blank=True)

    # Adding the 31/08/2023
    electronique_11n = models.CharField('BPGA HARD BOITIER PROTECTION ALIMENT RESEAU ELEC [FR]', max_length=200, blank=True)
    electronique_41n = models.CharField('BPGA FOURN.NO.SERIE BOITIER PROTECT ALIMENT RESEAU ELEC[FR]', max_length=200, blank=True)
    electronique_51n = models.CharField('BPGA FOURN.DATE.FAB- BOITIER PROTECT ALIMENT RESEAU ELEC[FR]', max_length=200, blank=True)
    electronique_61n = models.CharField('BPGA FOURN.CODE - BOITIER PROTECTION ALIMENT RESEAU ELEC[FR]', max_length=200, blank=True)

    class Meta:
        verbose_name = "données CORVET"
        ordering = ['vin']

    @classmethod
    def hw_search(cls, value, all_data=True):
        if value is not None and len(value) == 10:
            value = value.strip()
            if not value[-2:].isdigit():
                value = value[:-2] + '77'
            for field in CORVET_HW_FILTERS:
                queryset = cls.objects.filter(**{field: value})
                if queryset:
                    return queryset
        if all_data:
            return cls.objects.all()
        return cls.objects.none()

    @classmethod
    def search(cls, value):
        if value is not None:
            query = value.strip()
            queryset = cls.hw_search(value, all_data=False)
            if queryset:
                return queryset
            filters = CORVET_FILTERS + CORVET_SN_FILTERS
            for field in filters:
                queryset = cls.objects.filter(**{field: query})
                if queryset:
                    return queryset
        return cls.objects.none()

    @classmethod
    def get_vehicles(cls, hardware: str) -> list:
        queryset = cls.hw_search(hardware, all_data=False)
        vehicles = []
        if queryset:
            queryset = queryset.order_by('donnee_ligne_de_produit')
            data = list(queryset.values_list('donnee_ligne_de_produit', flat=True).distinct())
            # data = list(set([query.donnee_ligne_de_produit for query in queryset]))
            for key in data:
                vehicles.append(dict(CorvetChoices.vehicles(True)).get(key, key))
        return vehicles

    def get_brand_display(self):
        value = self.donnee_marque_commerciale
        return dict(CorvetChoices.brands()).get(value, value)

    def get_vehicle_display(self):
        value = self.donnee_ligne_de_produit
        try:
            value = dict(CorvetChoices.vehicles()).get(value, value)
            data = literal_eval(value)
            if isinstance(data, dict):
                brand = self.get_brand_display()
                value = data.get(brand, f"{brand}_{self.donnee_ligne_de_produit}")
        except Exception:
            pass
        return value

    def __str__(self):
        return self.vin


class CorvetProduct(models.Model):
    corvet = models.OneToOneField('psa.Corvet', related_name='prods', on_delete=models.CASCADE, primary_key=True)

    # Multimedia
    radio = models.ForeignKey('Multimedia', related_name='corvet_radio', on_delete=models.SET_NULL, limit_choices_to={'type': 'RAD'}, null=True, blank=True)
    btel = models.ForeignKey('Multimedia', related_name='corvet_btel', on_delete=models.SET_NULL, limit_choices_to={'type': 'NAV'}, null=True, blank=True)
    ivi = models.ForeignKey('Multimedia', related_name='corvet_ivi', on_delete=models.SET_NULL, limit_choices_to={'type': 'NAV'}, null=True, blank=True)

    # ECU
    bsi = models.ForeignKey('psa.Ecu', related_name='corvet_bsi', on_delete=models.SET_NULL, limit_choices_to={'type': 'BSI'}, null=True, blank=True)
    vsm1 = models.ForeignKey('psa.Ecu', related_name='corvet_vsm1', on_delete=models.SET_NULL, limit_choices_to={'type': 'VSM1'}, null=True, blank=True)
    emf = models.ForeignKey('psa.Ecu', related_name='corvet_emf', on_delete=models.SET_NULL, limit_choices_to={'type': 'EMF'}, null=True, blank=True)
    cmm = models.ForeignKey('psa.Ecu', related_name='corvet_cmm', on_delete=models.SET_NULL, limit_choices_to={'type': 'CMM'}, null=True, blank=True)
    bsm = models.ForeignKey('psa.Ecu', related_name='corvet_bsm', on_delete=models.SET_NULL, limit_choices_to={'type': 'BSM'}, null=True, blank=True)
    hdc = models.ForeignKey('psa.Ecu', related_name='corvet_hdc', on_delete=models.SET_NULL, limit_choices_to={'type': 'HDC'}, null=True, blank=True)
    cmb = models.ForeignKey('psa.Ecu', related_name='corvet_cmb', on_delete=models.SET_NULL, limit_choices_to={'type': 'CMB'}, null=True, blank=True)
    fmux = models.ForeignKey('psa.Ecu', related_name='corvet_fmux', on_delete=models.SET_NULL, limit_choices_to={'type': 'FMUX'}, null=True, blank=True)
    mds = models.ForeignKey('psa.Ecu', related_name='corvet_mds', on_delete=models.SET_NULL, limit_choices_to={'type': 'MDS'}, null=True, blank=True)
    cvm2 = models.ForeignKey('psa.Ecu', related_name='corvet_cvm2', on_delete=models.SET_NULL, limit_choices_to={'type': 'CVM2'}, null=True, blank=True)
    vmf = models.ForeignKey('psa.Ecu', related_name='corvet_vmf', on_delete=models.SET_NULL, limit_choices_to={'type': 'VMF'}, null=True, blank=True)
    dmtx = models.ForeignKey('psa.Ecu', related_name='corvet_dmtx', on_delete=models.SET_NULL, limit_choices_to={'type': 'DMTX'}, null=True, blank=True)
    bpga = models.ForeignKey('psa.Ecu', related_name='corvet_bpga', on_delete=models.SET_NULL, limit_choices_to={'type': 'BPGA'}, null=True, blank=True)

    class Meta:
        verbose_name = "produits CORVET"
        ordering = ['corvet']

    def __str__(self):
        return self.corvet.vin


class CorvetOption(models.Model):
    corvet = models.OneToOneField('psa.Corvet', related_name='opts', on_delete=models.CASCADE, primary_key=True)
    tag = models.CharField('tag', max_length=100, blank=True)
    update = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Options CORVET"
        ordering = ['corvet']

    def __str__(self):
        return self.corvet.vin


class CorvetAttribute(models.Model):
    key_1 = models.CharField('cle1', max_length=100)
    key_2 = models.CharField('cle2', max_length=100)
    label = models.CharField('libellé', max_length=500)
    col_ext = models.CharField('colext', max_length=10)

    class Meta:
        verbose_name = "Attributs CORVET"
        ordering = ['id']

    def __str__(self):
        return f"{self.key_1}_{self.key_2} - {self.label}"


class ProductChoice(models.Model):
    MODEL_CHOICES = [('MULTIMEDIA', 'Multimédia'), ('ECU', 'Calculateur')]
    PROTO_CHOICES = [('AEE2004', 'AEE2004'), ('AEE2010', 'AEE2010')]

    name = models.CharField('Nom', max_length=200, unique=True)
    family = models.CharField('Famille', max_length=50, choices=MODEL_CHOICES)
    short_name = models.CharField('Nom court', max_length=20)
    ecu_type = models.CharField('Type ECU', max_length=10)
    cal_attribute = models.CharField('Attribut CAL', max_length=3, blank=True)
    protocol = models.CharField('Protocole', max_length=100, choices=PROTO_CHOICES, blank=True)
    uce_code = models.CharField('UCE Code', max_length=2, blank=True)
    unlock_key = models.CharField('Unlock Key', max_length=4, blank=True)
    supplier = models.ForeignKey('psa.SupplierCode', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Choix produit"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'uce_code', 'unlock_key', 'supplier'], name="Product choice unique")
        ]

    def __str__(self):
        value = f"{self.name}"
        if self.protocol:
            value = value + f"_{self.protocol}"
        if self.supplier:
            value = value + f"_{self.supplier}"
        return value.replace(' ', '_')


class Multimedia(models.Model):
    MEDIA_CHOICES = [
        ('N/A', 'Vide'),
        ('HDD', 'Disque Dur'), ('EMMC', 'eMMC'), ('external SD', 'Carte SD Externe'),
        ('8Go', 'Carte SD 8Go'), ('16Go', 'Carte SD 16Go'), ('8Go 16Go', 'Carte SD 8 ou 16 Go'),
    ]
    LVDS_CON_CHOICES = [(1, '1'), (2, '2'), (3, '3'), (4, '4')]
    USB_CON_CHOICES = [(1, '1'), (2, '2'), (3, '3')]
    ANT_CON_CHOICES = [(1, '1'), (2, '2'), (3, '3')]

    comp_ref = models.BigIntegerField('réf. comp. matériel', primary_key=True)
    mat_ref = models.CharField('réf. matériel', max_length=10, blank=True)
    label_ref = models.CharField('réf. étiquette', max_length=10, blank=True)
    product = models.ForeignKey('psa.ProductChoice', related_name='medias', on_delete=models.SET_NULL, limit_choices_to={'family': 'MULTIMEDIA'}, null=True, blank=True)
    name = models.CharField('modèle', max_length=20, blank=True)
    xelon_name = models.CharField('modèle Xelon', max_length=100, blank=True)
    oe_reference = models.CharField('référence OEM', max_length=200, blank=True)
    supplier_oe = models.CharField("fabriquant", max_length=50, blank=True)
    pr_reference = models.CharField("référence PR", max_length=10, blank=True)
    type = models.CharField('type', max_length=3)
    level = models.CharField('niveau', max_length=100, blank=True)
    extra = models.CharField('supplément', max_length=100, blank=True)
    flash_nor = models.CharField('flashNOR', max_length=100, blank=True)
    flash_nand = models.CharField('flashNAND', max_length=100, blank=True)
    emmc = models.CharField('eMMC', max_length=100, blank=True)
    dab = models.BooleanField('DAB', default=False)
    cam = models.BooleanField('caméra de recul', default=False)
    cd_player = models.BooleanField('lecteur CD', default=False)
    jukebox = models.BooleanField('jukebox', null=True)
    carplay = models.BooleanField('CarPlay', null=True)
    media = models.CharField('type de média', max_length=20, choices=MEDIA_CHOICES, blank=True)
    lvds_con = models.IntegerField("nombre d'LVDS", choices=LVDS_CON_CHOICES, null=True, blank=True)
    ant_con = models.IntegerField("Nombre d'antenne", choices=ANT_CON_CHOICES, null=True, blank=True)
    usb_con = models.IntegerField("nombre d'USB", choices=USB_CON_CHOICES, null=True, blank=True)
    front_pic = models.ImageField(upload_to='psa', blank=True)
    setplate_pic = models.ImageField(upload_to='psa', blank=True)
    rear_pic = models.ImageField(upload_to='psa', blank=True)
    relation_by_name = models.BooleanField('relation par nom', default=False)
    firmware = models.ForeignKey('Firmware', on_delete=models.SET_NULL, limit_choices_to={'is_active': True}, null=True, blank=True)

    class Meta:
        verbose_name = "Données Multimédia"
        ordering = ['comp_ref']

    def get_type_display(self):
        dict_type = dict(BTEL_TYPE_CHOICES)
        return dict_type.get(self.type, "")

    def get_name_display(self):
        dict_name = dict(BTEL_PRODUCT_CHOICES)
        return dict_name.get(self.name, "")

    def __iter__(self):
        for field in self._meta.fields:
            yield field.verbose_name.capitalize(), field.value_to_string(self)

    def __str__(self):
        return f"{self.comp_ref}_{self.name}_{self.level}_{self.type}"


class Firmware(models.Model):
    update_id = models.CharField('SWL(UpdateID)', max_length=18, unique=True)
    version = models.CharField('UpdateVersion', max_length=200)
    type = models.CharField('UpdateType', max_length=100, blank=True)
    version_date = models.DateField('MediaVersionDate', null=True, blank=True)
    ecu_type = models.CharField('EcuType', max_length=50)
    url = models.URLField('lien de téléchargement', max_length=500, blank=True)
    is_active = models.BooleanField('actif', default=False)

    class Meta:
        verbose_name = "Firmwares Télématique"
        ordering = ['-update_id']

    def __str__(self):
        return f"{self.version}_{self.ecu_type}"


class Calibration(models.Model):
    factory = models.CharField('version usine', max_length=10, unique=True)
    type = models.CharField('type', max_length=3)
    current = models.CharField('version actuelle', max_length=10, blank=True)
    pr_reference = models.CharField('référence PR', max_length=10, blank=True)
    is_available = models.BooleanField('disponible', default=False)

    def get_type_display(self):
        dict_type = dict(CAL_TYPE_CHOICES)
        return dict_type.get(self.type, "")

    @classmethod
    def get_cal_file(cls, value):
        data = dict()
        queryset = cls.objects.exclude(is_available=False).filter(Q(factory=value) | Q(current=value))
        if queryset:
            types = list(queryset.order_by('type').values_list('type', flat=True).distinct())
            for value in types:
                currents = queryset.filter(type=value).order_by('current')
                data[value.lower()] = list(currents.values_list('current', flat=True).distinct())
        return data

    class Meta:
        verbose_name = "Calibration"
        ordering = ['-factory']

    def __str__(self):
        return self.factory


class Ecu(models.Model):
    comp_ref = models.CharField("réf. comp. matériel", max_length=10, unique=True)
    mat_ref = models.CharField("réf. matériel", max_length=10, blank=True)
    label_ref = models.CharField('réf. étiquette', max_length=10, blank=True)
    name = models.CharField("nom du modèle", max_length=50, blank=True)
    xelon_name = models.CharField('modèle Xelon', max_length=100, blank=True)
    product = models.ForeignKey('psa.ProductChoice', related_name='ecus', on_delete=models.SET_NULL, limit_choices_to={'family': 'ECU'}, null=True, blank=True)
    type = models.CharField('type', max_length=10)
    first_barcode = models.CharField('premier code-barres', max_length=200, blank=True)
    second_barcode = models.CharField('deuxième code-barres', max_length=200, blank=True)
    hw = models.CharField('HW', max_length=10, blank=True)
    sw = models.CharField('SW', max_length=10, blank=True)
    supplier_oe = models.CharField("fabriquant", max_length=50, blank=True)
    pr_reference = models.CharField("référence PR", max_length=10, blank=True)
    extra = models.CharField('supplément', max_length=100, blank=True)
    relation_by_name = models.BooleanField('relation par nom', default=False)

    class Meta:
        verbose_name = "Données ECU"
        ordering = ['comp_ref']

    def get_type_display(self):
        dict_type = dict(ECU_TYPE_CHOICES)
        return dict_type.get(self.type, "")

    def get_name_display(self):
        return self.name

    def __iter__(self):
        for field in self._meta.fields:
            yield field.verbose_name.capitalize(), field.value_to_string(self)

    def __str__(self):
        return f"{self.comp_ref}_{self.name}"


class SupplierCode(models.Model):
    code = models.CharField('code', max_length=4, primary_key=True)
    name = models.CharField('nom fournisseur', max_length=200)

    class Meta:
        verbose_name = "Code Fournisseur"
        ordering = ['code']

    def __str__(self):
        return self.name


class DefaultCode(models.Model):
    code = models.CharField('code', max_length=5)
    description = models.CharField('description', max_length=500)
    type = models.CharField('type', max_length=2)
    characterization = models.CharField('caractérisation', max_length=500, blank=True)
    location = models.CharField('localisation', max_length=500, blank=True)
    help = models.CharField('aide', max_length=500, blank=True)
    ecu_type = models.CharField('type ECU', max_length=100)

    class Meta:
        verbose_name = "Code Defaut"
        ordering = ['code']
        constraints = [
            models.UniqueConstraint(fields=['code', 'type', 'ecu_type'], name="Default code unique")
        ]

    def __str__(self):
        return f"{self.code} {self.type} {self.ecu_type}"


class Vehicle(models.Model):
    name = models.CharField('modèle', max_length=50, unique=True)
    brand = models.CharField('fabriquant', max_length=50)

    def __str__(self):
        return f"{self.brand} {self.name}"


class CanRemote(models.Model):
    label = models.CharField('label', max_length=20)
    location = models.IntegerField('position')
    type = models.CharField('Type commande', max_length=10)
    product = models.CharField('produit', max_length=50, blank=True)
    can_id = models.CharField('can_id', max_length=20)
    dlc = models.IntegerField('DLC', default=8)
    data = models.CharField('data', max_length=500)
    vehicles = models.ManyToManyField('psa.Vehicle', blank=True)

    def getcan(self):
        if ',' in self.data:
            return f"WS+GETCAN={self.can_id},{self.data}"
        if re.match(r'^B[0-7].\d{2}$', str(self.data)):
            pos, value = self.data[1:].split('.')
            data = ",".join(["0x00" if _ != int(pos) else f"0x{value}" for _ in range(self.dlc)])
            return f"WS+GETCAN={self.can_id},{data}"
        return ""

    @classmethod
    def get_volume(cls, product, vehicle):
        queryset = cls.objects.filter(product=product, vehicles__name__icontains=vehicle).distinct()
        vol_list = []
        for label in ['VOL+', 'VOL-']:
            try:
                vol_list.append(queryset.get(label=label))
            except cls.DoesNotExist:
                vol_list.append(None)
        return vol_list

    def save(self, *args, **kwargs):
        data_list = self.data.split(',')
        if self.dlc == 0:
            self.dlc = len(data_list)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Télécommande CAN"
        ordering = ['location']
        constraints = [
            models.UniqueConstraint(fields=['label', 'type', 'product', 'can_id', 'data'], name="Can remote unique")
        ]

    def __str__(self):
        return f"{self.label} {self.type} {self.can_id} {self.data}"
