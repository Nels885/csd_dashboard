import os
import re
from constance import config as conf

from . import current as config


CSD_ROOT = os.path.abspath(os.path.expanduser(conf.BASE_DIR[0]) + conf.BASE_DIR[1:])

XLS_RASPEEDI_FILE = os.path.join(CSD_ROOT, conf.XLS_RASPEEDI_FILE)
XLS_SQUALAETP_FILE = os.path.join(CSD_ROOT, conf.XLS_SQUALAETP_FILE)
XLS_ATTRIBUTS_FILE = os.path.join(CSD_ROOT, conf.XLS_ATTRIBUTS_FILE)
XLS_DELAY_FILES = [os.path.join(CSD_ROOT, file) for file in config.xls_delay_files]
CSV_EXTRACTION_FILE = os.path.join(CSD_ROOT, conf.CSV_EXTRACTION_FILE)
XLS_ECU_REF_BASE = os.path.join(CSD_ROOT, conf.XLS_ECU_REF_BASE)

XML_PATH = os.path.join(CSD_ROOT, config.xml_extract_dir)

TAG_PATH = os.path.join(CSD_ROOT, config.tag_dir)
TAG_LOG_PATH = os.path.join(CSD_ROOT, config.tag_log_dir)

DICT_YEAR = config.dict_year


def string_to_list(separators, string):
    """ format a character string into a list """
    return [value.strip() for value in re.split(separators, string)]
