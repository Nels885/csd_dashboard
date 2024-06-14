#!/usr/bin/env bash
#
# CSD Dashboard
# setup script
#       Author: Lionel VOIRIN (Nels885)

set -e

cat << "EOF"
 ________  ________  ________          ________  ________  ________  ___  ___  ________  ________  ________  ________  ________
|\   ____\|\   ____\|\   ___ \        |\   ___ \|\   __  \|\   ____\|\  \|\  \|\   __  \|\   __  \|\   __  \|\   __  \|\   ___ \
\ \  \___|\ \  \___|\ \  \_|\ \       \ \  \_|\ \ \  \|\  \ \  \___|\ \  \\\  \ \  \|\ /\ \  \|\  \ \  \|\  \ \  \|\  \ \  \_|\ \
 \ \  \    \ \_____  \ \  \ \\ \       \ \  \ \\ \ \   __  \ \_____  \ \   __  \ \   __  \ \  \\\  \ \   __  \ \   _  _\ \  \ \\ \
  \ \  \____\|____|\  \ \  \_\\ \       \ \  \_\\ \ \  \ \  \|____|\  \ \  \ \  \ \  \|\  \ \  \\\  \ \  \ \  \ \  \\  \\ \  \_\\ \
   \ \_______\____\_\  \ \_______\       \ \_______\ \__\ \__\____\_\  \ \__\ \__\ \_______\ \_______\ \__\ \__\ \__\\ _\\ \_______\
    \|_______|\_________\|_______|        \|_______|\|__|\|__|\_________\|__|\|__|\|_______|\|_______|\|__|\|__|\|__|\|__|\|_______|
             \|_________|                                    \|_________|
EOF

cat << EOF
Open source
Copyright 2022-$(date +'%Y'), CSD Dashboard Web Application
https://github.com/Nels885, https://bitbucket.org/Nels885

===================================================

EOF

# Setup

CYAN='\033[0;36m'
RED='\033[31m'
NC='\033[0m' # No Color

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

COREVERSION="1.0.0"

echo "setup.sh version $COREVERSION"

# Take the Url proxy
URL_PROXY=""

# Functions

function proxy() {
  read -p "Url proxy (if empty no proxy): " URL_PROXY
  echo "Use proxy: $URL_PROXY"
  pip3 config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
  pip3 config set global.proxy $URL_PROXY
}

function aptInstall() {
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
  sudo pip3 install pipenv
  pipenv --python 3
  pipenv sync
}

function pipenvUpdate() {
  echo -e "${RED}Updating Pipenv Environment...${NC}"
  pipenv sync
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

function checkPythonVersion() {
  python3 --version
}


function listCommands() {
cat << EOT
Available commands:

install
start
restart
update
stop
help

See more at https://github.com/Nels885/csd_dashboard/

EOT
}

# Commands

checkPythonVersion

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
    proxy
    aptInstall
    pipenvInstall
    ;;
  "update")
    proxy
    aptUpgrade
    pipenvUpdate
    ;;
  "help")
    listCommands
    ;;
  *)
    echo -e "${RED}No command found.${NC}"
    echo
    listCommands
esac
