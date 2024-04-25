######################
# CanRemote Model

PROD_CHOICES = [('', '---'), ('RT6', 'RT6'), ('SMEG', 'SMEG'), ('NAC', 'NAC'), ('IVI', 'IVI')]

######################
# Ecu Model

ECU_TYPE_CHOICES = [
    ('BSI', 'Boitier Servitude Intelligent'), ('VSM1', 'Module Supervision Vehicule'),
    ('BSM', 'Boitier Servitude Moteur'),
    ('CMB', 'Combine Planche de Bord'), ('CMM', 'Calculateur Moteur Multifonction'),
    ('EMF', 'Ecran Multifonctions'), ('FMUX', 'Façade Multiplexée'),
    ('HDC', 'Haut de Colonne de Direction (COM200x)'), ('MDS', 'Module de service telematique'),
    ('CVM2', 'Camera Video Multifonction V2'), ('VMF', 'Module Commutation Integre'),
    ('DMTX', 'Dispositif Maintien Tension'), ('BPGA', 'Boitier Protection Alimentation Reseau Elec')
]

#####################
# Multimedia Model

BTEL_PRODUCT_CHOICES = [
    ('RD3', 'RD3'), ('RD4', 'RD4'), ('RD45', 'RD45'), ('RD5', 'RD5'), ('RD6', 'RD6'), ('RDE', 'RDE'),
    ('RT3', 'RT3'), ('RT4', 'RT4'), ('RT5', 'RT5'), ('RT6', 'RT6 / RNEG2'), ('RT6v2', 'RT6v2 / RNEG2'),
    ('SMEG', 'SMEG'), ('SMEGP', 'SMEG+ / SMEG+ IV1'), ('SMEGP2', 'SMEG+ IV2'),
    ('NG4', 'NG4'), ('RNEG', 'RNEG'), ('RCC', 'RCC'),
    ('NAC1', 'NAC wave1'), ('NAC2', 'NAC wave2'), ('NAC3', 'NAC wave3'), ('NAC4', 'NAC wave4'),
    ('IVI', 'In-Vehicle Infotainment')
]

BTEL_TYPE_CHOICES = [('RAD', 'Radio'), ('NAV', 'Navigation')]

#####################
# Calibration Model

CAL_TYPE_CHOICES = [
    ('', '---'),
    ('94B', 'BSI SOFT - Boitier Servitude Intelligent'), ('94A', 'CMM SOFT - Calculateur Moteur Multifonction'),
    ('94F', 'RADIO SOFT - Recepteur Radio'), ('94K', 'CMB SOFT - Combine Planche de Bord'),
    ('94L', 'EMF SOFT - Ecran Multifonctions'), ('94X', 'BTEL SOFT - Boitier Telematique'),
    ('96B', 'BSM SOFT - Boitier Servitude Moteur'), ('99H', 'MDS SOFT - Module de service telematique'),
    ('92Y', 'CVM2_2_ SOFT - CAMERA VIDEO MULTIFONCTION V2'),
    ('99K', 'ARTIV SOFT - Boitier Aide au Respect du Temps Inter Vehicule'),
    ('92E', 'AVM - SOFT - AIDE VISUELLE A LA MANŒUVRE'), ('96L', 'DAE SOFT - Direction Assistee Electrique')
]


def convert(tup, di):
    di = dict(tup)
    return di
