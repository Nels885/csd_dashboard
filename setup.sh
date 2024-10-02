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
SCRIPTS_DIR="$DIR/scripts"

COREVERSION="1.0.1"

echo "setup.sh version $COREVERSION"

# Take the Url proxy
URL_PROXY=""

# Functions

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
    $SCRIPTS_DIR/run.sh start
    ;;
  "restart")
    $SCRIPTS_DIR/run.sh restart
    ;;
  "stop")
    $SCRIPTS_DIR/run.sh stop
    ;;
  "install")
    $SCRIPTS_DIR/run.sh install
    ;;
  "update")
    $SCRIPTS_DIR/run.sh update
    ;;
  "help")
    listCommands
    ;;
  *)
    echo -e "${RED}No command found.${NC}"
    echo
    listCommands
esac
