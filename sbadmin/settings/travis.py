from . import *

SECRET_KEY = 'q2sb*vqltbpi59f#l2c&mak*%h&xzv1)i^#e0_as^cmx^-9)8x'

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'travis_ci_test',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
