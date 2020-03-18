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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
