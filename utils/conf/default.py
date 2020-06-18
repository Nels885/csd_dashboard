# Config Clarion

base_dir = "~/Documents/CSD_DATABASE"

xls_raspeedi_file = "PROG/RASPEEDI/table_boitier_PSA.xlsx"
xls_squalaetp_file = "EXTS/squalaetp.xls"
xls_attributs_file = "EXTS/Attributs CORVET.xlsx"
csv_extraction_file = "EXTS/extraction.csv"
xls_ecu_cross_reference = "ETUDES/CALCULATEUR/CALCULATEUR MOTEUR/_REMAN_ECU/ECU_Cross_reference_list 20200312.xlsx"
xls_ecu_ref_base = "Base réf ECU.xlsx"

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

dict_year = {
    2020: 'C', 2021: 'D', 2022: 'G', 2023: 'H', 2024: 'K', 2025: 'L', 2026: 'O', 2027: 'T', 2028: 'U',
    2029: 'V', 2030: 'W',
}

#####################
# MQTT configuration
#####################

MQTT_TEMP_ADJ = 4
MQTT_CLIENT = None
MQTT_USER = None
MQTT_PSWD = None
MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 1883
KEEP_ALIVE = 45

ecu_email_list = ['test@test.com']
