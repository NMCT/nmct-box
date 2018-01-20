#!/usr/bin/env bash
#
# Install dependencies and NMCT Box services

if [[ $EUID -eq 0 ]]; then
  printf "This script should be run as a regular user with sudo access, but NOT root!" $0 >&2
  exit 1
fi

if ! sudo -v; then
  exit 1
fi

set -o errexit

[[ -z ${NMCT_HOME} ]] && export NMCT_HOME="$(dirname "${PWD}")"
echo "Installing to ${NMCT_HOME}"
readonly PYENV="${NMCT_HOME}/env/bin/python"

# dependencies
readonly APT_PACKAGES="python3-dev python3-venv swig libatlas-base-dev scons libffi-dev portaudio19-dev python3-pyaudio sox libssl-dev nginx python3-notebook"
readonly NPM_PACKAGES="configurable-http-proxy"
readonly PIP_PACKAGES="setuptools wheel"


install_apt_packages(){
    sudo apt update -y
    sudo apt install -y ${APT_PACKAGES}
}

install_npm_packages(){
    sudo apt install -y npm
    sudo npm install -g ${NPM_PACKAGES}
}

create_venv(){
    python3 -m venv "${NMCT_HOME}/env"
    ${PYENV} -m pip install --upgrade pip ${PIP_PACKAGES}
}

install_aiy_voicekit(){
    # pull & install AIY drivers
    dir="$(dirname "${NMCT_HOME}")/aiy-voicekit"
    git clone https://github.com/google/aiyprojects-raspbian.git "${dir}"
    pushd "${dir}"
    git checkout aiyprojects
    sed -i 's#/home/pi/AIY-projects-python/##' ./scripts/install-deps.sh
    chmod +x ./scripts/*.sh
    ./scripts/install-deps.sh
    sudo ./scripts/install-services.sh
    sudo ./scripts/configure-driver.sh
    sudo ./scripts/install-alsa-config.sh
    popd
    pushd "${dir}/src"
    ${PYENV} setup.py install
    popd
}

install_snowboy(){
    # pull & install Snowboy
    dir="$(dirname "${NMCT_HOME}")/snowboy"
    git clone https://github.com/Kitt-AI/snowboy.git ${dir}
    pushd ${dir}
    ${PYENV} setup.py build install
    popd
}

install_neopixel(){
    # pull & install NeoPixel driver
    dir="$(dirname "${NMCT_HOME}")/rpi-ws821x"
    git clone https://github.com/jgarff/rpi_ws281x.git ${dir}
    sed -i 's/^\(\#define GPIO_PIN\W*\)18$/\112/g' "${dir}/main.c"
    pushd ${dir} && scons && popd
    pushd ${dir}/python
    ${PYENV} setup.py build install
    popd
}

install_nmct_box(){
    # install our package(s)
    pushd "${NMCT_HOME}/src"
    ${PYENV} -m pip install -r requirements.txt
    ${PYENV} setup.py install
    popd
}

#deactivate
#sudo -s

install_services(){
    for file in ${NMCT_HOME}/systemd/*; do
        cat ${file} | envsubst | sudo tee "/etc/systemd/system/$(basename ${file})"
    #    systemctl daemon-reload
        sudo systemctl enable "$(basename ${file})"
    #    systemctl start "$(basename ${file})"
    done

    if [[ -f /etc/nginx/sites-enabled/default ]]; then
        sudo rm /etc/nginx/sites-enabled/default
    fi

    cat "${NMCT_HOME}/resources/conf/nginx" | envsubst '${NMCT_HOME}' | sudo tee /etc/nginx/sites-available/nmct-box

    if [[ ! -f /etc/nginx/sites-enabled/nmct-box ]]; then
        sudo ln -s /etc/nginx/sites-available/nmct-box /etc/nginx/sites-enabled/nmct-box
    fi
    #systemctl restart nginx
}



install_apt_packages
install_npm_packages
create_venv
install_aiy_voicekit
install_snowboy
install_neopixel
install_nmct_box
install_services

printf "Done. If you just installed the AIY drivers for the first time, reboot and run '%s/aiy-voicekit/checkpoints/check_audio.py'\n" ${NMCT_HOME}