#!/usr/bin/env bash
set -e

# Setup

CYAN='\033[0;36m'
RED='\033[31m'
NC='\033[0m' # No Color

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."
SCRIPTS_DIR="$DIR/scripts"
URL_PROXY=""

# Take the user
read -p "Enter the User Linux (default): " USER

if [ $USER == ""]
then
  USER=$(whoami)
fi
echo "User Linux: $USER"

USER_DIR="/home/$USER"


echo -e "${CYAN}DIR=$DIR - USER=$USER ${NC}"


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
  echo -e "${RED}Install Pipenv Environment...${NC}"
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
  pipenv sync
}

function supervisorUpdate() {
  $SCRIPTS_DIR/generate_files.sh $USER
  echo -e "${RED}Supervisor configuration update...${NC}"
  sudo mv -v /tmp/csddashboard-daphne.conf /etc/supervisor/conf.d/
  sudo mv -v /tmp/celery.conf /etc/supervisor/conf.d/
  sudo supervisorctl reread
  sudo supervisorctl update
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

function envConfiguration() {
  # Take the user
  read -p "Put into production [y/N]: " CHOICE

  if [[ "$CHOICE" == [Yy]* ]]
    echo -e "${RED}Installing needed programs for production...${NC}"
    sudo http_proxy=$URL_PROXY apt install -y supervisor nginx

    supervisorUpdate
  then
    echo -e "${RED}Installing needed programs for production...${NC}"
    sudo http_proxy=$URL_PROXY apt install -y postgresql postgresql-contrib
  fi
}

function install() {
  setProxy
  aptInstall
  pipenvInstall
  envConfiguration
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
    setProxy
    aptUpgrade
    pipenvUpdate
    ;;
  "help")
    listCommands
    ;;
esac
