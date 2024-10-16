import os
import re
import ast
from constance import config as conf


def string_to_list(string, separators=",|;"):
    """ format a character string into a list """
    if isinstance(string, list):
        return string
    return [value.strip() for value in re.split(separators, string) if len(string) != 0]


def string_to_dict(string):
    """ Format a character string into a dictionary """
    return ast.literal_eval(string)


def get_path(filename=None, path=None) -> str:
    # Paths to network drives
    if not path:
        if len(conf.CSD_DIR) > 1:
            path = os.path.abspath(os.path.expanduser(conf.CSD_DIR[0]) + conf.CSD_DIR[1:])
        else:
            path = conf.CSD_DIR
    if isinstance(filename, str):
        try:
            return os.path.join(path, str(conf.__getattr__(filename)))
        except AttributeError:
            pass
    return path


# Paths to network drives
if len(conf.CSD_DIR) > 1:
    CSD_ROOT = os.path.abspath(os.path.expanduser(conf.CSD_DIR[0]) + conf.CSD_DIR[1:])
else:
    CSD_ROOT = conf.CSD_DIR

if len(conf.NAS_DIR) > 1:
    NAS_ROOT = os.path.abspath(os.path.expanduser(conf.NAS_DIR[0]) + conf.NAS_DIR[1:])
else:
    NAS_ROOT = conf.NAS_DIR

# Paths CSD and NAS
EXTS_PATHS, ROOT_PATHS = [os.path.join(CSD_ROOT, "EXTS")], [CSD_ROOT]
if NAS_ROOT:
    EXTS_PATHS.append(os.path.join(NAS_ROOT, "EXTS"))
    ROOT_PATHS.append(NAS_ROOT)


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
