# Config Clarion

base_dir = "~/Documents/CSD_DATABASE"

xls_raspeedi_file = "PROG/RASPEEDI/table_boitier_PSA.xlsx"
xls_squalaetp_file = "EXTS/squalaetp.xls"
xls_attributs_file = "EXTS/Attributs CORVET.xlsx"

xls_delay_files = [
    "RH/AnalyseRetards/PSA.xls",
    "RH/AnalyseRetards/ILOTAUTRE.xls",
    "RH/AnalyseRetards/LaboQual.xls",
    "RH/AnalyseRetards/DEFAUT.xls",
    "RH/AnalyseRetards/CLARION.xls"
]

xml_extract_dir = "LOGS/CORVET_XML_TEST"

prod_log_dir = {
    'SMEG': {
        'raspeedi': ['LOGS/LOG_RASPEEDI/SMEG', 'LOGS/LOG_RASPEEDI/SMEGP', 'LOGS/LOG_RASPROG/SMEG',
                     'LOGS/LOG_RASPROG/SMEGP'],
        'cal': ['LOGS/LOG_CAL_SMEG'],
    },
    'RT': {
        'raspeedi': ['LOGS/LOG_RASPEEDI'],
        'cal': ['LOGS/LOG_CAL_RT6', 'LOGS/LOG_CAL_RTx'],
    },
    'RD': {
        'cal': ['LOGS/LOG_CAL_RD45', 'LOGS/LOG_CAL_RD6', 'LOGS/LOG_CAL_RDx'],
    }
}

tag_log_dir = "LOGS/LOG_CONFIG_PROD"
tag_dir = "LOGS/CALIBRE"
