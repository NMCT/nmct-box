#!/usr/bin/env bash

set -o errexit

declare -r CREATE_USER=nmct
declare -r PASSWORD=smartthings
declare -r HOSTNAME_PREFIX="nmct-box"


declare -rx NMCT_HOME="/home/${CREATE_USER}/nmct-box"
source "$(dirname "${BASH_SOURCE}")/nmct-box.sh"
#readonly PYENV="${NMCT_HOME}/env/bin/python"

update_raspbian
do_system_settings
change_hostname ${HOSTNAME_PREFIX}
new_default_user ${CREATE_USER} ${PASSWORD}
sudo -E su ${CREATE_USER}
git clone https://github.com/nmctseb/nmct-box.git "${NMCT_HOME}"
create_venv "${NMCT_HOME}/env"
source "${NMCT_HOME}/env/bin/activate"
source "$(dirname "${BASH_SOURCE}")/install.sh"


echo -e "\n\n\n\nDone! User 'pi' will be disabled, after rebooting you can connect with: \n
    hostname:\t\033[32m${new_hostname}\033[0m
    username:\t\033[32m${CREATE_USER}\033[0m
    password:\t\033[32m${PASSWORD}\033[0m
    \nPress any key to reboot...\n\n\n"
read -sn 1
sudo chage -E 0 pi
sudo usermod -L pi
#rm -f "${BASH_SOURCE}"
sudo reboot
