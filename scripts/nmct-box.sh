#!/usr/bin/env bash

##################################################################
# Installation Defaults                                          #
##################################################################
#                                                                #
declare -r NEW_USER=nmct                                      #
declare -r PASSWORD=smartthings                                  #
declare -r HOSTNAME_PREFIX="box"                                 #
declare -r DEFAULT_HOME=/home/nmct/nmct-box                      #
declare -r REPO_URL="https://github.com/NMCT/nmct-box.git"    #
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
    ${cmd} do_boot_behaviour B3 #B1=console, B3=Desktop, n+1=autologon
    ${cmd} do_boot_wait ${FALSE}
    ${cmd} do_boot_splash ${TRUE}
    ${cmd} do_vnc ${TRUE}

    # interfaces
    ${cmd} do_ssh ${TRUE}
    ${cmd} do_spi ${TRUE}
    ${cmd} do_i2c ${TRUE}
    ${cmd} do_onewire ${TRUE}

    echo "alias ll='ls -al'" | sudo tee /etc/profile.d/nmct_box.sh
}

#    function install_framework(){
#        su - nmct<<EOF
#    git clone https://github.com/nmctseb/nmct-box.git "${NMCT_HOME}"
#    chmod +x "${NMCT_HOME}"/scripts/*.sh
#    source "${NMCT_HOME}"/scripts/install.sh
#    EOF
#    }

function install_packages(){
    echo -e "Installing apt packages from $1"
    sudo apt update -y
    grep -v '#' $(realpath "${1}") | xargs sudo apt-get install -y
}

function install_npm_packages(){
    echo -e "Installing npm packages $1"
    sudo apt install -y npm
    sudo npm install -g ${@}
}

function create_venv(){
    echo -e "Setting up venv in $1"

    python3 -m pip install --upgrade pip wheel setuptools
    python3 -m venv --system-site-packages ${1}
    ${1}/bin/python -m pip install -I setuptools
    # FIXME!
#    echo 'export PATH="'${1}'/bin:$PATH"' | tee -a ~/.bashrc >> ~/.xsessionrc
}

function install_aiy_voicekit(){
    echo -e "Installing AIY voicekit to $1"
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
    mv ~/.asoundrc ~/.asoundrc.bak
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
    if [[ ${1} -eq ${TRUE} ]]; then
        echo -e "Enabling pi user"
        sudo chage -E -1 pi
        sudo usermod -U pi
    else
        echo -e "Disabling pi user"
        sudo chage -E 1 pi
        sudo usermod -L pi
   fi
}
function install_snowboy(){
    # pull & install Snowboy
    dir="$1"
    echo -e "Installing snowboy in $dir"

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
    echo -e "Pull & install NeoPixel driver"
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
    echo -e "Installing systemd units"
    for file in "${1}/systemd/"*; do
        cat ${file} | envsubst | sudo tee "/etc/systemd/system/$(basename ${file})" >/dev/null
        sudo systemctl enable "$(basename ${file})"
    done

    if [[ -a /etc/nginx/sites-enabled/default ]]; then
        sudo rm -f /etc/nginx/sites-enabled/default
    fi

    cat "${1}/resources/conf/nginx" | envsubst '${NMCT_HOME} ${USER}' |
        sudo tee /etc/nginx/sites-available/nmct-box >/dev/null

    if [[ ! -f /etc/nginx/sites-enabled/nmct-box ]]; then
        sudo ln -s /etc/nginx/sites-available/nmct-box /etc/nginx/sites-enabled/nmct-box
    fi
}

##################################################################
# Purpose: Links this script to /usr/bin
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
#   $2 -> Destination directory (default: /usr/bin)
# #################################################################
function install_nmct_tool(){
    echo -e "Installing nmct-box tool "
    dst=${2}; dst="$(realpath "${dst:=/usr/bin}")/nmct-box"
    echo "Installing tool to ${dst}..."
    if [[ -a ${dst} ]]; then
        sudo rm -f ${dst}
    fi
    sudo ln -fs "${1}/scripts/nmct-box.sh" ${dst}
}
##################################################################
# Purpose: Start/stop/restart NMCT-box systemd services units
# Arguments:
#   $1 -> Action: start|stop|restart|status|enable|disable
#   $1 -> Service: flask|jupyter|jupyterhub|bokeh|ipcheck
# #################################################################
function do_services(){
    action=${1}; action=${action:=status}
    service=${2}; service=${service:=*}
    echo -e "Service $service $action"

    sudo systemctl daemon-reload
    for svc in /etc/systemd/system/nmct-box-${service}; do
#        echo "sudo systemctl ${action} "$(basename ${svc})""
        sudo systemctl ${action} "$(basename "${svc}")"
    done
    sudo systemctl ${action} nginx
}

##################################################################
# Purpose: Add NMCT Box desktop shortcuts
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function configure_desktop(){
    echo -e "Installing shortcuts"
    sudo mkdir -p /usr/share/nmct-wallpaper
    sudo ln -sf ${1}/src/nmct/web/static/media/NMCT-*.png /usr/share/nmct-wallpaper/
#    echo 'DISPLAY='':0.0'' pcmanfm  --set-wallpaper /usr/share/nmct-wallpaper/NMCT-1920x1200.png' >> ~/.xsessionrc

    for file in ${1}/shortcuts/*; do
        echo ${file}
        #cat ${file} | envsubst '${NMCT_HOME} ${USER}' > ${file}  #"~/Desktop/$(basename "${file}")"
        envsubst '${NMCT_HOME} ${USER}' < ${file}  > ~/Desktop/$(basename "${file}")
#        ln -sf $(realpath "${file}") ~/Desktop/$(basename "${file}")
    done
}

##################################################################
# Purpose: Set default values so git doesn't complain when stashing
# Arguments: None
# #################################################################
function do_git_config(){
    echo -e "Setting git config"

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
    echo "export NMCT_HOME=${4}" | sudo tee -a /etc/profile.d/nmct_box.sh >/dev/null
    do_git_config
}

##################################################################
# Purpose: Install system packages, create and activate
#  virtual environment
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function prepare_install(){
    echo "export NMCT_HOME=${1}" | sudo tee -a /etc/profile.d/nmct_box.sh >/dev/null
    do_git_config
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
    install_snowboy "$(dirname "${1}")/snowboy"
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
    ./env/bin/python3 -m pip install -r requirements.txt -e .
    ./env/bin/python -m ipykernel install --user --name nmct-box-env --display-name "Python (nmct-box)"
    sudo mkdir -p /home/nmct/uploads/static
    sudo chown -R www-data:www-data /home/nmct/uploads
    sudo chmod -R g+w  /home/nmct/uploads
    mkdir -p ./src/nmct/web/run
    sudo chmod -R g+w  ./src/nmct/web/run
    mkdir -p ./.secret
    cp ./resources/credentials-template.json ./.secret/credentials.json
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
    install_nmct_tool "${1}"
    install_services "${1}"
    configure_desktop "${1}"
    do_services start '*'
    do_services enable '*'

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
}

function apply_update(){
    do_services stop
    install_framework "${1}"
    install_services "${1}"
    configure_desktop "${1}"
    do_services start '*'
}
function apply_refresh(){
    pushd "${1}"
    install_services "${1}"
    configure_desktop "${1}"
    do_services restart '*'
}

##################################################################
# Purpose: Add and connect to WPA secured WiFi network
# Arguments:
#   $1 -> Install directory (NMCT_HOME)
# #################################################################
function add_wifi_psk(){
    ssid=${1}
    psk=${2}
    test -z "${psk}"  && echo "Usage: ${0} connect <SSID> <PSK>" >&2 && exit 1
    wpa_passphrase "${1}" "${2}" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf
    wpa_cli -i wlan0 reconfigure
    wpa_cli -i wlan0 status
}

##################################################################
# Command line use
# #################################################################

function do_phase1(){
    NMCT_HOME=${DEFAULT_HOME}
    prepare_image ${HOSTNAME_PREFIX} ${NEW_USER} ${PASSWORD} ${DEFAULT_HOME}
    sudo -u ${NEW_USER} git clone "${REPO_URL}" "${1}"
    install_nmct_tool "${DEFAULT_HOME}"

    [[ -z ${SSH_CONNECTION} ]] &&
        ip="$(ip a s scope global up | awk '/inet /{print substr($2,0)}' | tr '\n' '\t' )" ||
        ip="$(echo ${SSH_CONNECTION} | awk '{print $3}')"
    echo -e "\n\n\n\nDone! User 'pi' will be disabled, after rebooting you can connect with: \n
    address:\t\033[32m${ip}\033[0m
    hostname:\t\033[32m${new_hostname}\033[0m
    username:\t\033[32m${NEW_USER}\033[0m
    password:\t\033[32m${PASSWORD}\033[0m
    \nPress any key to reboot...\n\n\n"
    read -sn 1
    do_pi_user ${FALSE}
    }

function set_boot_script() {
#FIXME

    sudo cp "${1}/systemd/nmct-box-atboot.service" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable nmct-box-atboot.service
    sudo systemctl start nmct-box-atboot.service
    echo -e "#!/usr/bin/env bash \n\n ${1}/scipts/nmct-box.sh install; exit $?" |
        sudo tee /boot/atboot.sh >/dev/null

}

function usage(){
    echo -e "$(basename "${0}"): NMCT Box installation and management tool"
    echo -e "Usage: \033[21m$(basename "${0}")\033[0m \033[1m<command>\033[0m [options]"

    echo -e "\nInstallation:"
    echo -e "\t \033[1m prepare \033[0m\t Prepare a freshly installed Raspbian OS"
    echo -e "\t \033[1m install \033[0m\t Download and install the framework and all its dependencies"
    echo -e "\t \033[1m reinstall \033[0m\t Delete the entire installation and reinstall including dependencies"
    echo -e "\t \033[1m autoinstall \033[0m\t Prepare fresh OS and schedule install at next boot"
    echo -e "\t \033[1m set-hostname \033[0m\t Auto-configure hostname"

    echo -e "\nServices:"
    echo -e "\t \033[1m start \033[0m\t Start all associated services "
    echo -e "\t \033[1m stop \033[0m\t\t Start all associated services "
    echo -e "\t \033[1m restart \033[0m\t Restart all associated services "
    echo -e "\t \033[1m status \033[0m\t Show status of associated services "
    echo -e "\t \033[1m enable \033[0m\t Configure all associated services for automatic startup "
    echo -e "\t \033[1m disable \033[0m\t Disable automatic startup for all associated services"
    echo -e "\t \033[1m run <service> \033[0m\t Run single service in foreground for debugging"

    echo -e "\nUpdating:"
    echo -e "\t \033[1m update \033[0m\t Download and install updates, including dependencies"
    echo -e "\t \033[1m refresh \033[0m\t Download and install updates of the framework only"

    echo -e "\Misc:"
    echo -e "\t \033[1m connect <ssid> <passphrase> \033[0m\t Connect to WPA-PSK secured WiFi network"
    echo -e "\t \033[1m develop \033[0m\t Checkout dev branch"

    exit 0
}

if [[ -z "$@" ]]; then
    usage
fi

NMCT_HOME="${NMCT_HOME:=$PWD}"
echo -e "\nNMCT-Box home: ${NMCT_HOME}\n"
source "${NMCT_HOME}/env/bin/activate"

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
    set-hostname)
        change_hostname ${HOSTNAME_PREFIX}
    ;;
    start|stop|restart|status|enable|disable)
        do_services ${@}
        exit $?
    ;;
    run)
        shift
        $(grep ExecStart /etc/systemd/system/nmct-box-${@}.service | cut -d '=' -f2)
        exit $?
    ;;
    update|refresh)
        arg=${@}
        do_services stop
        update_project "${NMCT_HOME}"
        "$0" -f apply_${arg} "${NMCT_HOME}"
        do_services start '*'
        exit $?
    ;;
    reload)
        do_services stop
        pushd "${NMCT_HOME}"
        ./env/bin/python -m pip install -e .
        popd
        do_services start
    ;;
    develop)
        pushd "${NMCT_HOME}"
        git fetch
        git add .
        git stash
        git checkout -b dev --track origin/dev
    ;;
    connect)
        shift
        add_wifi_psk "${@}"
        exit $?
    ;;
    --function|-f)
        shift
        "${@}"
        exit $?
    ;;
    --help|-h)
        usage
        exit 0
    ;;
    *)
        die "Unknown command: ${i}. See ${0} --help for details."
    ;;
    esac
done
