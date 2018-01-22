#!/usr/bin/env bash

##################################################################
# Installation Defaults                                          #
##################################################################
#                                                                #
declare -r CREATE_USER=nmct                                      #
declare -r PASSWORD=smartthings                                  #
declare -r HOSTNAME_PREFIX="box"                                 #
declare -r DEFAULT_HOME=/home/nmct/nmct-box                      #
declare -r REPO_URL="https://github.com/nmctseb/nmct-box.git"    #
#                                                                #
##################################################################
#                                                                #
##################################################################

#
#
#
#
#
#

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
    echo -e "Changed hostname to \033[32m${new_hostname}\033[0m. Please reboot to apply the change.\n\n"
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
#        sudo systemctl daemon-reload
#        sudo systemctl enable "$(basename ${file})"
#        sudo systemctl start "$(basename ${file})"
    done

    if [[ -a /etc/nginx/sites-enabled/default ]]; then
        sudo rm -f /etc/nginx/sites-enabled/default
    fi

    cat "${1}/resources/conf/nginx" | envsubst '${NMCT_HOME} ${USER}' | sudo tee /etc/nginx/sites-available/nmct-box

    if [[ ! -f /etc/nginx/sites-enabled/nmct-box ]]; then
        sudo ln -s /etc/nginx/sites-available/nmct-box /etc/nginx/sites-enabled/nmct-box
    fi
#    sudo systemctl restart nginx
}

##################################################################
# Purpose: Links this script to /usr/bin
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
#   $2 -> Destination directory (default: /usr/bin)
# #################################################################
function install_nmct_tool(){
    dst=${1}; dst="$(realpath "${dst:=/usr/bin}")/nmct-box"
    echo "Installing tool to ${dst}..."
    if [[ -a ${dst} ]]; then
        sudo rm -f ${dst}
    fi
    sudo ln -s "${1}/scripts/nmct-box.sh" ${dst}
}
##################################################################
# Purpose: Start/stop/restart NMCT-box systemd services units
# Arguments:
#   $1 -> Action: start|stop|restart|status|enable|disable
#   $1 -> Service: flask|jupyter|jupyterhub|bokeh|ipcheck
# #################################################################
function do_service(){
    action=${1}; action=${action:=status}
    service=${2}; service=${action:=*}

    sudo systemctl daemon-reload
    for svc in /etc/systemd/system/nmct-box-${service}; do
        sudo systemctl ${action} "$(basename ${svc})"
    done
        sudo systemctl ${action} nginx
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
# Purpose: Set default values so git doesn't complain when stashing
# Arguments: None
# #################################################################
function do_git_config(){
    git config --global user.name "NMCT-Box"
    git config --global user.email "box@nmct.be"

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
    echo "export NMCT_HOME=${4}" | sudo tee -a /etc/profile.d/nmct_box.sh
    do_git_config
}

##################################################################
# Purpose: Install system packages, create and activate
#  virtual environment
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function prepare_install(){
    echo "export NMCT_HOME=${1}" | sudo tee -a /etc/profile.d/nmct_box.sh
    git clone ${REPO_URL} "${1}"
    install_packages "${1}/packages.txt"
    create_venv "${1}/env"
    source "${1}/env/bin/activate"
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
    python3 -m pip install .
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
    do_service start
    do_service enable

}

##################################################################
# Purpose: Update/refresh framework
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function update_project(){
    pushd "${1}"
    git add .
    git stash
    git pull
    source "${1}/scripts/nmct-box.sh"
}

function apply_update(){
    install_framework "${1}"
    install_services "${1}"
    install_shortcuts "${1}"
    do_service restart
}
function apply_refresh(){
    pushd "${1}"
    python3 -m pip install .
    install_services "${1}"
    install_shortcuts "${1}"
    do_service restart
}




##################################################################
# Command line use
# #################################################################

function do_phase1(){
    prepare_image ${HOSTNAME_PREFIX} ${CREATE_USER} ${PASSWORD} ${DEFAULT_HOME}
    echo -e "\n\n\n\nDone! User 'pi' will be disabled, after rebooting you can connect with: \n
    hostname:\t\033[32m${new_hostname}\033[0m
    username:\t\033[32m${CREATE_USER}\033[0m
    password:\t\033[32m${PASSWORD}\033[0m
    \nPress any key to reboot...\n\n\n"
    read -sn 1
    do_pi_user ${FALSE}
    }

function set_boot_script() {
#TODO
    install_nmct_tool "${1}"
    sudo cp "${1}/systemd/nmct-box-atboot.service" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable nmct-box-atboot.service
    sudo systemctl start nmct-box-atboot.service
    echo -e "/usr/bin/env bash \n\n source "

}

function usage(){
    echo -e "$(basename "${0}"): NMCT Box installation and management tool"
    echo -e "Usage: \033[21m$(basename "${0}")\033[0m \033[1m<command>\033[0m [options]"

    echo -e "\nInstallation:"
    echo -e "\t \033[1m prepare \033[0m\t Prepare a freshly installed Raspbian OS"
    echo -e "\t \033[1m install \033[0m\t Download and install the framework and all its dependencies"
    echo -e "\t \033[1m reinstall \033[0m\t Delete the entire installation and reinstall including dependencies"
    echo -e "\t \033[1m autoinstall \033[0m\t Prepare fresh OS and schedule install at next boot"

    echo -e "\nServices:"
    echo -e "\t \033[1m start \033[0m\t Start all associated services "
    echo -e "\t \033[1m stop \033[0m\t\t Start all associated services "
    echo -e "\t \033[1m restart \033[0m\t Restart all associated services "
    echo -e "\t \033[1m status \033[0m\t Show status of associated services "
    echo -e "\t \033[1m enable \033[0m\t Configure all associated services for automatic startup "
    echo -e "\t \033[1m disable \033[0m\t Disable automatic startup for all associated services"

    echo -e "\nUpdating:"
    echo -e "\t \033[1m update \033[0m\t Download and install updates, including dependencies"
    echo -e "\t \033[1m refresh \033[0m\t Download and install updates of the framework only"

    echo -e ""
    exit 0
}

if [[ -z "$@" ]]; then
    usage
fi

NMCT_HOME="${NMCT_HOME:=$PWD}"
echo -e "\nNMCT-Box home: ${NMCT_HOME}\n"
for i in $*; do
    case ${i} in
    prepare)
        do_phase1
        sudo reboot
    ;;
    install)
        install_nmct_box "${NMCT_HOME}"
        printf "Done. If you just installed the AIY drivers for the first time, reboot and run '%s/aiy-voicekit/checkpoints/check_audio.py'\n" ${NMCT_HOME}
        exit $?
    ;;
    reinstall)
        sudo rm -rf "${NMCT_HOME}"
        install_nmct_box "${NMCT_HOME}"
    ;;
    autoinstall)
        do_phase1
        set_boot_script "${NMCT_HOME}"
    ;;
    start|stop|restart|status|enable|disable)
        shift
        do_service ${@}
        exit $?
    ;;
    update|refresh)
        update_project "${NMCT_HOME}"
        apply_${@} "${NMCT_HOME}"
        exit $?
    ;;
    --function)
        shift
        "${@}"
        exit $?
    ;;
    --help|-h)
        usage ${0}
                exit 0
    ;;
    *)
        die "Unknown command: ${i}. See ${0} --help for details."
    ;;
    esac
done
