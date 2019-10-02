import os

# Config Clarion

XLS_ROOT = os.path.abspath(os.path.expanduser('~') + '/Documents/CSD_DATABASE')

XLS_RASPEEDI_FILE = os.path.join(XLS_ROOT, "PROG/RASPEEDI/table_boitier_PSA.xlsx")
XLS_SQUALAETP_FILE = os.path.join(XLS_ROOT, "EXTS/squalaetp.xls")
XLS_ATTRIBUTS_FILE = os.path.join(XLS_ROOT, "EXTS/Attributs CORVET.xlsx")
XLS_DELAY_FILES = [
    os.path.join(XLS_ROOT, "RH/AnalyseRetards/PSA.xls"),
    os.path.join(XLS_ROOT, "RH/AnalyseRetards/ILOTAUTRE.xls"),
    os.path.join(XLS_ROOT, "RH/AnalyseRetards/LaboQual.xls"),
    os.path.join(XLS_ROOT, "RH/AnalyseRetards/DEFAUT.xls"),
    os.path.join(XLS_ROOT, "RH/AnalyseRetards/CLARION.xls"),
]

XML_PATH = os.path.join(XLS_ROOT, 'LOGS/CORVET_XML_TEST')

# Test d'écriture du fichier de configuration
# Saut de ligne.
