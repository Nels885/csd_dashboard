#!/usr/bin/env bash
set -e

# Setup
CYAN='\033[0;36m'
RED='\033[31m'
NC='\033[0m' # No Color

cat << EOF > $PROG_DIR/.env
DJANGO_SETTINGS_MODULE=sbadmin.settings.production
EOF

# Generate production.py file
echo -e "${RED}Settings of Django for production...${NC}"

read -p "Secret Key for Django: " SECRET_KEY
echo "Database Port: $SECRET_KEY"

read -p "Database name (default: csd_atelier): " DB_NAME
[[ "$DB_NAME" == "" ]] && DB_NAME="csd_atelier"
echo "Database Name: $DB_NAME"

read -p "Database user (default: csdadmin): " DB_USER
[[ "$DB_USER" == "" ]] && DB_USER="csdadmin"
echo "Database Name: $DB_USER"

read -p "Database password (default: empty): " DB_PWD
echo "Database password: $DB_PWD"

read -p "Database host (default: localhost): " DB_HOST
[[ "$DB_HOST" == "" ]] && DB_HOST="localhost"
echo "Database Host: $DB_HOST"

read -p "Database port (default: 5432): " DB_PORT
[[ "$DB_PORT" == "" ]] && DB_PORT="5432"
echo "Database Port: $DB_PORT"

read -p "Database port (default: <prog_dir>/media/): " MEDIA_ROOT
[[ "$MEDIA_ROOT" == "" ]] && MEDIA_ROOT="%PROG_DIR/media/"
echo "Database Port: $MEDIA_ROOT"

cat << EOF > $PROG_DIR/sbadmin/settings/production.py
from . import *

SECRET_KEY = '$SECRET_KEY'

DEBUG = False

ALLOWED_HOSTS = []


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '$DB_NAME',
        'USER': '$DB_USER',
        'PASSWORD': '$DB_PWD',
        'HOST': '$DB_HOST',
        'PORT': '$DB_PORT',
    }
}

# CELERY STUFF
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'

MEDIA_ROOT = '$MEDIA_ROOT'
EOF