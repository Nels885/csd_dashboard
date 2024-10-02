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


cat << EOF > /tmp/csddashboard-daphne.conf
[program:csddashboard-daphne]
command=pipenv run daphne sbadmin.asgi:application
user=$USER
directory=$PROG_DIR
autostart=true
autorestart=unexpected
startsecs=0
startretries=10
EOF


cat << EOF > /tmp/celery.conf
[program:celery-django]
command=pipenv run celery -A sbadmin worker --loglevel=info
user=$USER
directory=$PROG_DIR
autostart=true
numprocs=1
autorestart=unexpected
startsecs=0
startretries=10
priority=999

[program:celery-beat]
command=pipenv run celery -A sbadmin beat -l info -S django
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
