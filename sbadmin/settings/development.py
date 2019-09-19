from . import *

SECRET_KEY = 'q2sb*vqltbpi59f#l2c&mak*%h&xzv1)i^#e0_as^cmx^-9)8x'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'csd_atelier',
        'USER': 'nels885',
        'PASSWORD': 'kikoulol',
        'HOST': '',
        'PORT': '5432',
    }
}

INTERNAL_IPS = '127.0.0.1'

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
