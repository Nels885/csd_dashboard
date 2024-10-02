#!/usr/bin/env bash
set -e

# Setup
CYAN='\033[0;36m'
RED='\033[31m'
NC='\033[0m' # No Color

PROG_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."

USER=$(whoami)
if [ $# -gt 0 ]
then
    USER=$1
fi
USER_DIR="/home/$USER"


cat << EOF > /tmp/csddashboard-daphne.conf
[program:csddashboard-daphne]
command=$USER_DIR/.local/bin/pipenv run daphne sbadmin.asgi:application
user=$USER
directory=$PROG_DIR
autostart=true
autorestart=unexpected
startsecs=0
startretries=10
EOF


cat << EOF > /tmp/celery.conf
[program:celery-django]
command=$USER_DIR/.local/bin/pipenv run celery -A sbadmin worker --loglevel=info
user=$USER
directory=$PROG_DIR
autostart=true
numprocs=1
autorestart=unexpected
startsecs=0
startretries=10
priority=999

[program:celery-beat]
command=$USER_DIR/.local/bin/pipenv run celery -A sbadmin beat -l info -S django
user=$USER
directory=$PROG_DIR
autostart=true
numprocs=1
autorestart=unexpected
startsecs=0
startretries=10
priority=999
EOF


cat << EOF > $PROG_DIR/.env
DJANGO_SETTINGS_MODULE=sbadmin.settings.production
EOF

# Generate production.py file
echo -e "${RED}Settings of Django for production...${NC}"

read -p "Secret Key for Django: " SECRET_KEY
echo "Database Port: $SECRET_KEY"

read -p "Database name (default: csdatelier): " DB_NAME
[[ "$DB_NAME" == "" ]] && DB_NAME="csdatelier"
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
