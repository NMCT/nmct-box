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
