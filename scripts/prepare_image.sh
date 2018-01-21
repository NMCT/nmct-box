#!/usr/bin/env bash

set -o errexit

declare -rx NMCT_HOME="/home/nmct/nmct-box"
declare -r CREATE_USER=nmct
declare -r PASSWORD=smartthings
declare -r HOSTNAME_PREFIX="nmct-box"

source ./nmct-box.sh

do_system_settings
new_hostname=$(change_hostname ${HOSTNAME_PREFIX})
new_default_user ${CREATE_USER} ${PASSWORD}
update_raspbian



echo -e "\n\n\n\nDone! User 'pi' will be disabled, after rebooting you can connect with: \n
    hostname:\t\033[32m${new_hostname}\033[0m
    username:\t\033[32m${CREATE_USER}\033[0m
    password:\t\033[32m${PASSWORD}\033[0m
    \nPress any key to reboot...\n\n\n"
read -sn 1
chage -E 0 pi
usermod -L pi
rm -f "${BASH_SOURCE}"
reboot
