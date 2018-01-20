#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
     printf "This script should be run as root, try 'sudo %s'\n" ${0} >&2
     exit 1
fi

set -o errexit

export NMCT_HOME="/home/nmct/nmct-box"
readonly new_user=nmct
readonly new_pass=smartthings


readonly APT_PACKAGES="etckeeper vim lsof telnet dnsutils at screen git ufw"

update_raspbian(){
    apt update -y &&
    apt install -y ${APT_PACKAGES}
    apt full-upgrade -y --autoremove
}

create_user(){
    echo "Creating user ${new_user}"
    cp -R /home/pi/* /etc/skel # && chown -R root:root /etc/skel/*
    groups=$(id pi -Gn | sed 's/^pi //g' | sed 's/ /,/g')
    useradd ${new_user} -s /bin/bash -m -G ${groups}
    echo "${new_user}:${new_pass}" | chpasswd
    sed "s/^pi/${new_user}/" /etc/sudoers.d/010_pi-nopasswd > "/etc/sudoers.d/011_${new_user}-nopasswd"
}

do_system_settings(){
    # system config
    echo "Updating system settings..."
    new_hostname="nmct-box-$(cut -d: -f4- < /sys/class/net/wlan0/address | tr -d :)"
    cmd='raspi-config nonint'
    ${cmd} do_hostname ${new_hostname}
    ${cmd} do_wifi_country 'BE'
    ${cmd} do_change_timezone 'Europe/Brussels'
    ${cmd} do_configure_keyboard 'be'
    ${cmd} do_boot_behaviour B1 #B1=console, B3=Desktop, n+1=autologon
    ${cmd} do_boot_wait 1
    ${cmd} do_boot_splash 1

    # interfaces
    ${cmd} do_ssh 0
    ${cmd} do_spi 0
    ${cmd} do_i2c 0
    ${cmd} do_onewire 0

    echo "export NMCT_HOME=${NMCT_HOME}" > /etc/profile.d/nmct_box.sh
    echo "alias ll='ls -al'" >> /etc/profile.d/nmct_box.sh
}


do_finish(){
    echo -e "\n\Done! User 'pi' will be disabled, after rebooting you can connect with: \n
        hostname: \t\t\033[32m${new_hostname}\033[0m
        user: \t\t\033[32m${new_user}\033[0m
        password:\t\t\033[32m${new_pass}\033[0m
        \nPress any key to reboot...\n"
    read -sn 1
    chage -E 0 pi
    rm -f "${BASH_SOURCE}"
    reboot
}


#########################################################

update_raspbian
create_user
do_system_settings

su - nmct<<EOF
git clone https://github.com/nmctseb/nmct-box.git "${NMCT_HOME}"
chmod +x "${NMCT_HOME}/scripts/*.sh"
source "${NMCT_HOME}/scripts/install.sh"
EOF

do_finish
