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


# Paths to network drives
if len(conf.BASE_DIR) > 1:
    CSD_ROOT = os.path.abspath(os.path.expanduser(conf.BASE_DIR[0]) + conf.BASE_DIR[1:])
else:
    CSD_ROOT = conf.BASE_DIR

if len(conf.NAS_DIR) > 1:
    NAS_ROOT = os.path.abspath(os.path.expanduser(conf.NAS_DIR[0]) + conf.NAS_DIR[1:])
else:
    NAS_ROOT = conf.NAS_DIR

# Paths CSD and NAS for EXTS folder
EXTS_PATHS = [os.path.join(CSD_ROOT, "EXTS")]
if NAS_ROOT:
    EXTS_PATHS.append(os.path.join(NAS_ROOT, "EXTS"))


XLS_DELAY_PATH = os.path.join(CSD_ROOT, conf.XLS_DELAY_PATH)
XML_CORVET_PATH = os.path.join(CSD_ROOT, conf.XML_CORVET_PATH)

TAG_XELON_PATH = os.path.join(CSD_ROOT, conf.TAG_XELON_PATH)
TAG_XELON_LOG_PATH = os.path.join(CSD_ROOT, conf.TAG_XELON_LOG_PATH)
TAG_XELON_TEL_PATH = os.path.join(CSD_ROOT, conf.TAG_XELON_TEL_PATH)

# Paths to network files
XLS_RASPEEDI_FILE = os.path.join(CSD_ROOT, conf.XLS_RASPEEDI_FILE)
XLS_SQUALAETP_FILE = os.path.join(CSD_ROOT, conf.XLS_SQUALAETP_FILE)
XLS_ATTRIBUTS_FILE = os.path.join(CSD_ROOT, conf.XLS_ATTRIBUTS_FILE)
XLS_DELAY_FILES = [os.path.join(XLS_DELAY_PATH, file) for file in string_to_list(conf.XLS_DELAY_FILES)]
XLS_TIME_LIMIT_FILE = os.path.join(CSD_ROOT, conf.XLS_TIME_LIMIT_FILE)
CSV_EXTRACTION_FILE = os.path.join(CSD_ROOT, conf.CSV_EXTRACTION_FILE)

DICT_YEAR = string_to_dict(conf.DICT_YEAR)
