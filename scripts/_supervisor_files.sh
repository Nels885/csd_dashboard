#!/usr/bin/env bash
set -e

# Setup
CYAN='\033[0;36m'
RED='\033[31m'
NC='\033[0m' # No Color

USER=$(whoami)
if [ $# -gt 0 ]
then
    USER=$1
fi
USER_DIR="/home/$USER"

PROG_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."
if [ $# -gt 1 ]
then
    PROG_DIR=$2
fi

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



