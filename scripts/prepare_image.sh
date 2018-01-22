#!/usr/bin/env bash

set -o errexit

declare -r CREATE_USER=nmct
declare -r PASSWORD=smartthings
declare -r HOSTNAME_PREFIX="nmct-box"


declare -rx NMCT_HOME="/home/${CREATE_USER}/nmct-box"
source "$(dirname "${BASH_SOURCE}")/nmct-box.sh"
#readonly PYENV="${NMCT_HOME}/env/bin/python"

prepare_image
sudo -E su ${CREATE_USER}

install_nmct_box "${NMCT_HOME}"




sudo chage -E 0 pi
sudo usermod -L pi
#rm -f "${BASH_SOURCE}"
sudo reboot


   1  git clone https://github.com/nmctseb/nmct-box /tmp/nmct
    2  chmod ug+x /tmp/nmct/scripts/nmct-box.sh
    3  git config user.email 29257008+nmctseb@users.noreply.github.com
    4  cd /tmp/nmct/
    5  git commit
    6  git config --global user.email "29257008+nmctseb@users.noreply.github.com"
    7  git config --global user.name nmctseb
    8  git commit -am permissions
    9  git push origin master
