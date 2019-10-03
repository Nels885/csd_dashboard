import os
import shutil
from django.conf import settings

try:
    from . import current as config
except (ModuleNotFoundError, ImportError):
    shutil.copyfile(settings.CONF_DEFAULT_FILE, settings.CONF_FILE)
    from . import current as config


XLS_ROOT = os.path.abspath(os.path.expanduser(config.base_dir[0]) + config.base_dir[1:])

XLS_RASPEEDI_FILE = os.path.join(XLS_ROOT, config.xls_raspeedi_file)
XLS_SQUALAETP_FILE = os.path.join(XLS_ROOT, config.xls_squalaetp_file)
XLS_ATTRIBUTS_FILE = os.path.join(XLS_ROOT, config.xls_attributs_file)
XLS_DELAY_FILES = [os.path.join(XLS_ROOT, file) for file in config.xls_delay_files]

XML_PATH = os.path.join(XLS_ROOT, config.xml_extract_dir)
