import os

from . import current as config


CSD_ROOT = os.path.abspath(os.path.expanduser(config.base_dir[0]) + config.base_dir[1:])

XLS_RASPEEDI_FILE = os.path.join(CSD_ROOT, config.xls_raspeedi_file)
XLS_SQUALAETP_FILE = os.path.join(CSD_ROOT, config.xls_squalaetp_file)
XLS_ATTRIBUTS_FILE = os.path.join(CSD_ROOT, config.xls_attributs_file)
XLS_DELAY_FILES = [os.path.join(CSD_ROOT, file) for file in config.xls_delay_files]
CSV_EXTRACTION_FILE = os.path.join(CSD_ROOT, config.csv_extraction_file)
XLS_ECU_CROSS_REFERENCE = os.path.join(CSD_ROOT, config.xls_ecu_cross_reference)
XLS_ECU_REF_BASE = os.path.join(CSD_ROOT, config.xls_ecu_ref_base)

XML_PATH = os.path.join(CSD_ROOT, config.xml_extract_dir)

TAG_PATH = os.path.join(CSD_ROOT, config.tag_dir)
TAG_LOG_PATH = os.path.join(CSD_ROOT, config.tag_log_dir)

DICT_YEAR = config.dict_year

TEMP_ADJ = int(config.MQTT_TEMP_ADJ)
MQTT_CLIENT = config.MQTT_CLIENT
MQTT_USER = config.MQTT_USER
MQTT_PSWD = config.MQTT_PSWD
MQTT_BROKER = config.MQTT_BROKER
MQTT_PORT = config.MQTT_PORT
KEEP_ALIVE = config.KEEP_ALIVE
