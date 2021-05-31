import os
import re
import ast
from constance import config as conf


def string_to_list(string, separators=",|;"):
    """ format a character string into a list """
    if isinstance(string, list):
        return string
    return [value.strip() for value in re.split(separators, string)]


def string_to_dict(string):
    """ Format a character string into a dictionary """
    return ast.literal_eval(string)


CSD_ROOT = os.path.abspath(os.path.expanduser(conf.BASE_DIR[0]) + conf.BASE_DIR[1:])

XLS_DELAY_PATH = os.path.join(CSD_ROOT, conf.XLS_DELAY_PATH)

XLS_RASPEEDI_FILE = os.path.join(CSD_ROOT, conf.XLS_RASPEEDI_FILE)
XLS_SQUALAETP_FILE = os.path.join(CSD_ROOT, conf.XLS_SQUALAETP_FILE)
XLS_ATTRIBUTS_FILE = os.path.join(CSD_ROOT, conf.XLS_ATTRIBUTS_FILE)
XLS_DELAY_FILES = [os.path.join(XLS_DELAY_PATH, file) for file in string_to_list(conf.XLS_DELAY_FILES)]
CSV_EXTRACTION_FILE = os.path.join(CSD_ROOT, conf.CSV_EXTRACTION_FILE)
XLS_ECU_REF_BASE = os.path.join(CSD_ROOT, conf.XLS_ECU_REF_BASE)


XML_CORVET_PATH = os.path.join(CSD_ROOT, conf.XML_CORVET_PATH)

TAG_XELON_PATH = os.path.join(CSD_ROOT, conf.TAG_XELON_PATH)
TAG_XELON_LOG_PATH = os.path.join(CSD_ROOT, conf.TAG_XELON_LOG_PATH)

DICT_YEAR = string_to_dict(conf.DICT_YEAR)
