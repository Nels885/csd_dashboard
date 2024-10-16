#!/usr/bin/env bash
set -e

# Setup

CYAN='\033[0;36m'
RED='\033[31m'
NC='\033[0m' # No Color

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."
if [ $# -gt 1 ]
then
    DIR=$2
fi

SCRIPTS_DIR="$DIR/scripts"
URL_PROXY=""
PROD_ENV=0

# Take the user
read -p "Enter the User Linux (default): " USER
[[ "$USER" == "" ]] && USER=$(whoami)
echo "User Linux: $USER"

read -p "Put into production [y/N]: " CHOICE
[[ "$CHOICE" == [Yy]* ]] && PROD_ENV=1

USER_DIR="/home/$USER"


echo -e "${CYAN}DIR=$DIR - USER=$USER  - PROD_ENV=$PROD_ENV ${NC}"


# Functions

function setProxy() {
  read -p "Url proxy (if empty no proxy): " URL_PROXY
  echo "Use proxy: $URL_PROXY"
}

function aptInstall() {
  aptUpgrade
  echo -e "${RED}Installing needed programs...${NC}"
  sudo http_proxy=$URL_PROXY apt install -y python3-pip python3-dev libpq-dev redis-server
}

function aptUpgrade() {
  # Update raspbian and install programm utils
  echo -e "${RED}Updating linux system...${NC}"
  sudo http_proxy=$URL_PROXY apt update && sudo http_proxy=$URL_PROXY apt dist-upgrade -y
}

function pipenvInstall() {
  echo -e "${RED}Pip configuration...${NC}"
  pip3 config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
  pip3 config set global.proxy "$URL_PROXY"
  pip3 install pipenv --user
  source ~/.profile
  pipenv --python 3
  pipenv sync
  pip3 config set global.proxy ""
}

function pipenvUpdate() {
  echo -e "${RED}Updating Pipenv Environment...${NC}"
  pip3 config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
  pip3 config set global.proxy "$URL_PROXY"
  if [ $PROD_ENV == 1 ]
  then
    echo -e "${RED}Updating Pipenv Env production...${NC}"
    pipenv sync
  else
    echo -e "${RED}Updating Pipenv Env development...${NC}"
    pipenv sync --dev
  fi
}

function supervisorUpdate() {
  if [ $PROD_ENV == 1 ]
  then
    echo -e "${RED}Supervisor configuration update...${NC}"
    $SCRIPTS_DIR/_supervisor_files.sh $USER $DIR
    sudo mv -v /tmp/csddashboard-daphne.conf /etc/supervisor/conf.d/
    sudo mv -v /tmp/celery.conf /etc/supervisor/conf.d/
    sudo supervisorctl reread
    sudo supervisorctl update
  fi
}

function serviceStop() {
  echo -e "${RED}Stop services...${NC}"
  sudo supervisorctl stop all
  wait
}

function serviceStart() {
  echo -e "${RED}Start services...${NC}"
  sudo supervisorctl start all
  wait
}

function install() {
  [ $PROD_ENV == 1 ] && $SCRIPTS_DIR/_settings_files.sh $USER $DIR
  setProxy
  aptInstall
  pipenvInstall
  supervisorUpdate
  if [ $PROD_ENV == 1 ]
  then
    echo -e "${RED}Installing needed programs for production...${NC}"
    sudo http_proxy=$URL_PROXY apt install -y supervisor nginx

    # Generate static files and add permissions
    pipenv run ./manage.py collectstatic --clear --noinput
    sudo gpasswd -a www-data csdadmin
  else
    echo -e "${RED}Installing needed programs for development...${NC}"
    sudo http_proxy=$URL_PROXY apt install -y postgresql postgresql-contrib
  fi
}

function update() {
  setProxy
  aptUpgrade
  pipenvUpdate
  supervisorUpdate
}

# Commands

case $1 in
  "start")
    serviceStart
    ;;
  "restart")
    serviceStop
    serviceStart
    ;;
  "stop")
    serviceStop
    ;;
  "install")
    install
    ;;
  "update")
    update
    ;;
  "help")
    listCommands
    ;;
esac
