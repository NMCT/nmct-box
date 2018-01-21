#!/usr/bin/env bash

declare -r TRUE=0
declare -r FALSE=1


##################################################################
# Purpose: Display an error message and die
# Arguments:
#   $1 -> Message
#   $2 -> Exit status (optional)
##################################################################
function die()
{
    local m="$1"	# message
    local e=${2-1}	# default exit status 1
    echo -e "$m" >&2
    exit ${e}
}
##################################################################
# Purpose: Return true if script is executed by the root user
# Arguments: none
# Return: True or False
##################################################################
function is_root()
{
   [ $(id -u) -eq 0 ] && return ${TRUE} || return ${FALSE}
}

function ensure_root(){
    if [[ $EUID -ne 0 ]]; then
         die "This script should be run as root, try 'sudo %s'\n" ${0}
         exit 1
    fi

}

function ensure_sudo(){
    if [[ $EUID -eq 0 ]]; then
      printf "This script should be run as a regular user with sudo access, but NOT root!" $0 >&2
      exit 1
    fi

    if ! sudo -v; then
      exit 1
    fi
}

##################################################################
# Purpose: Return true $user exits in /etc/passwd
# Arguments: $1 (username) -> Username to check in /etc/passwd
# Return: True or False
##################################################################
function is_user_exits()
{
    local u="$1"
    grep -q "^${u}" /etc/passwd && return ${TRUE} || return ${FALSE}
}

##################################################################
# Purpose: Copies the pi user's home directory to /etc/skel,
#  creates a new user and copies group membership from pi,
#  and adds a NOPASSWD file in sudoers.d
# Arguments:
#   $1 -> Username
#   $2 -> Password
##################################################################
function new_default_user(){
    local user=${1}
    local pass=${2}
    echo "Creating user ${user}"
    sudo cp -R /home/pi/* /etc/skel # && chown -R root:root /etc/skel/*
    groups=$(id pi -Gn | sed 's/^pi //g' | sed 's/ /,/g')
    sudo useradd ${user} -s /bin/bash -m -G ${groups}
    echo "${user}:${pass}" | sudo chpasswd
    sudo sed "s/^pi/${user}/" /etc/sudoers.d/010_pi-nopasswd | sudo tee "/etc/sudoers.d/011_${user}-nopasswd"
}

function update_raspbian(){
    sudo apt update -y && updated=${TRUE}
    sudo apt full-upgrade -y --autoremove
}

function change_hostname(){
    local cmd='sudo raspi-config nonint'
    new_hostname="${1}-$(cut -d: -f4- < /sys/class/net/wlan0/address | tr -d :)"
    ${cmd} do_hostname ${new_hostname}
}

function do_system_settings(){
    # system config
    echo "Updating system settings..."
    local cmd='sudo raspi-config nonint'
    ${cmd} do_wifi_country 'BE'
    ${cmd} do_change_timezone 'Europe/Brussels'
    ${cmd} do_configure_keyboard 'be'
    ${cmd} do_boot_behaviour B1 #B1=console, B3=Desktop, n+1=autologon
    ${cmd} do_boot_wait ${FALSE}
    ${cmd} do_boot_splash ${FALSE}
    ${cmd} do_vnc ${TRUE}

    # interfaces
    ${cmd} do_ssh ${TRUE}
    ${cmd} do_spi ${TRUE}
    ${cmd} do_i2c ${TRUE}
    ${cmd} do_onewire ${TRUE}

    echo "alias ll='ls -al'" | sudo tee /etc/profile.d/nmct_box
}

#    function install_framework(){
#        su - nmct<<EOF
#    git clone https://github.com/nmctseb/nmct-box.git "${NMCT_HOME}"
#    chmod +x "${NMCT_HOME}"/scripts/*.sh
#    source "${NMCT_HOME}"/scripts/install.sh
#    EOF
#    }

function install_packages(){
    sudo apt update -y
    grep -v '#' $(realpath "${1}") | xargs sudo apt-get install -y
}

function install_npm_packages(){
    sudo apt install -y npm
    sudo npm install -g ${@}
}

function create_venv(){
    python3 -m pip install --upgrade pip wheel setuptools
    python3 -m venv --system-site-packages ${1}
    ${1}/bin/python -m pip install -I setuptools
}

function install_aiy_voicekit(){
    # pull & install AIY drivers
    dir="$1"
    if [[ ! -d "${dir}" ]]; then
        git clone https://github.com/google/aiyprojects-raspbian.git "${dir}"
        pushd "${dir}"
    else
        pushd "${dir}"
        git pull
    fi
    git checkout aiyprojects
    sed -i 's#/home/pi/AIY-projects-python/##' ./scripts/install-deps.sh
    chmod +x ./scripts/*.sh
    ./scripts/install-deps.sh
    sudo ./scripts/install-services.sh
    sudo ./scripts/configure-driver.sh
    sudo ./scripts/install-alsa-config.sh
    popd
    pushd "${dir}/src"
    python3 setup.py install
    popd
}

##################################################################
# Purpose: Change state of default user (pi)
# Arguments:
#   $1 -> Boolean: (en/dis)able
# #################################################################
function do_pi_user(){
    if [[ ${1} ]]; then
        sudo chage -E -1 pi
        sudo usermod -U pi
    else
        sudo chage -E 1 pi
        sudo usermod -L pi
   fi
}
function install_snowboy(){
    # pull & install Snowboy
    dir="$1"
    if [[ ! -d "${dir}" ]]; then
        git clone https://github.com/Kitt-AI/snowboy.git ${dir}
        pushd "${dir}"
    else
        pushd "${dir}"
        git pull
    fi
    python3 setup.py build install
    popd
}

function install_neopixel(){
    # pull & install NeoPixel driver
    dir="$1"
    if [[ ! -d "${dir}" ]]; then
        git clone https://github.com/jgarff/rpi_ws281x.git ${dir}
        pushd "${dir}"
    else
        pushd "${dir}"
        git pull
    fi
    sed -i 's/^\(\#define GPIO_PIN\W*\)18$/\112/g' main.c
    scons && popd
    pushd ${dir}/python
    python3 setup.py build install
    popd
}

##################################################################
# Purpose: Install NMCT Box systemd unit files
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function install_services(){
    for file in ${1}/systemd/*; do
        cat ${file} | envsubst | sudo tee "/etc/systemd/system/$(basename ${file})"
        sudo systemctl daemon-reload
        sudo systemctl enable "$(basename ${file})"
        sudo systemctl start "$(basename ${file})"
    done

    if [[ -f /etc/nginx/sites-enabled/default ]]; then
        sudo rm /etc/nginx/sites-enabled/default
    fi

    cat "${1}/resources/conf/nginx" | envsubst '${NMCT_HOME} ${USER}' | sudo tee /etc/nginx/sites-available/nmct-box

    if [[ ! -f /etc/nginx/sites-enabled/nmct-box ]]; then
        sudo ln -s /etc/nginx/sites-available/nmct-box /etc/nginx/sites-enabled/nmct-box
    fi
    sudo systemctl restart nginx
    sudo ln -s "${1}/scripts/nmct-box.sh" /usr/bin/nmct-box
}

##################################################################
# Purpose: Add NMCT Box desktop shortcuts
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function install_shortcuts(){
    for file in ${1}/shortcuts/*; do
        cp ${file} ~/Desktop/
    done
}

##################################################################
# Purpose: Prepare fresh Raspbian image
# Arguments:
#   $1 -> Hostname prefix (will be appended with MAC address)
#   $2 -> Username to create
#   $3 -> Password forv new user
# #################################################################
function prepare_image(){
    update_raspbian
    do_system_settings
    change_hostname ${1}
    new_default_user ${2} ${3}
}

##################################################################
# Purpose: Install system packages, create and activate
#  virtual environment
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function prepare_install(){
    git clone https://github.com/nmctseb/nmct-box.git "${1}"
    install_packages "${1}/packages.txt"
    create_venv "${1}/env"
    source "${1}/env/bin/activate"
    echo "export NMCT_HOME=${1}" | sudo tee -a /etc/profile.d/nmct_box.sh
}


##################################################################
# Purpose: Install AIY & NeoPixel dependencies
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function install_dependencies(){
    install_aiy_voicekit "$(dirname "${1}")/aiy-voicekit"
    install_neopixel "$(dirname "${1}")/neopixel"
#    install_snowboy "$(dirname "${1}")/snowboy"
    install_npm_packages configurable-http-proxy
}

##################################################################
# Purpose: Install NMCT Box framework
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function install_framework(){
    # install our package
    pushd "${1}"
    python3 -m pip install -r requirements.txt
    python3 setup.py install
#    echo "${NMCT_HOME}/src" > "${NMCT_HOME}/env/lib/python3.5/site-packages/nmct-box.pth"
    popd
}

##################################################################
# Purpose: Install NMCT Box venv + deps + framework + services
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function install_nmct_box(){
    prepare_install "${1}"
    install_dependencies "${1}"
    install_framework "${1}"
    install_services "${1}"
    install_shortcuts "${1}"
}


##################################################################
# Purpose: Install NMCT Box venv + deps + framework + services
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function update_nmct_box(){
    pushd "${1}"
    git pull
    install_framework "${1}"
    install_services "${1}"
    install_shortcuts "${1}"
}

###################################################################
# Command line options
# #################################################################
[[ -z ${NMCT_HOME} ]] && export NMCT_HOME="$(dirname "${PWD}")"

echo "NMCT-Box home: ${NMCT_HOME}"

for i in $*; do
    case ${i} in
    prepare)
        declare -r CREATE_USER=nmct
        declare -r PASSWORD=smartthings
        declare -r HOSTNAME_PREFIX="nmct-box"
        prepare_image
        echo -e "\n\n\n\nDone! User 'pi' will be disabled, after rebooting you can connect with: \n
        hostname:\t\033[32m${new_hostname}\033[0m
        username:\t\033[32m${CREATE_USER}\033[0m
        password:\t\033[32m${PASSWORD}\033[0m
        \nPress any key to reboot...\n\n\n"
        read -sn 1
        do_pi_user ${FALSE}
        sudo reboot
        ;;
    install)
        install_nmct_box "${NMCT_HOME}"
        exit $?
        ;;
    update)
        update_nmct_box "${NMCT_HOME}"
        exit $?
        ;;
    esac
done
