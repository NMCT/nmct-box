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

export NMCT_HOME="$(dirname "${PWD}")"
readonly VENVDIR="${NMCT_HOME}/env"
readonly TEMPDIR="/tmp/nmct-box"
readonly APT_PKG="python3-dev python3-venv swig libatlas-base-dev scons libffi-dev portaudio19-dev \
python3-pyaudio sox libssl-dev nginx ufw python3-notebook npm"
readonly NPM_PKG="configurable-http-proxy"
readonly PIP_PKG="setuptools wheel distutils"

# install APT packages
sudo apt update -y && apt install -y ${APT_PKG}

# install NPM packages
npm install -g ${NPM_PKG}

# create venv
python3 -m venv ${VENVDIR}
${VENVDIR}/bin/python -m pip install --upgrade pip ${PIP_PKG}
source ${VENVDIR}/bin/activate

# install Python packages
${VENVDIR}/bin/python -m pip install -r "${NMCT_HOME}/src/requirements.txt"


# pull & install AIY drivers
dir="${NMCT_HOME}/aiy-voicekit"
git clone https://github.com/google/aiyprojects-raspbian.git "${dir}"
pushd "${dir}"
git checkout aiyprojects
./scripts/install-deps.sh
sudo ./scripts/install-services.sh
sudo ./scripts/configure-driver.sh
sudo ./scripts/install-alsa-config.sh
pushd "${dir}/src"
${VENVDIR}/bin/python setup.py install
popd

# pull & install Snowboy
dir=${TEMPDIR}/snowboy
git clone https://github.com/Kitt-AI/snowboy.git ${dir}
pushd ${dir}
${VENVDIR}/bin/python setup.py build install
popd

# pull & install NeoPixel driver
dir=${TEMPDIR}/rpi-ws821x
git clone https://github.com/jgarff/rpi_ws281x.git ${dir}
pushd ${dir}
scons
pushd ${dir}/python
${VENVDIR}/bin/python setup.py build install

# install our package(s)
pushd "${NMCT_HOME}/src"
python setup.py install

deactivate

# install services
sudo -s
echo "export NMCT_HOME=${NMCT_HOME}" > /etc/profile.d/nmct_box.sh

for file in ${NMCT_HOME}/systemd/*; do
    cat ${file} | envsubst > "/etc/systemd/system/$(basename ${file})"
    systemctl daemon-reload
    systemctl enable "$(basename ${file})"
    systemctl start "$(basename ${file})"
done

if [[ -f /etc/nginx/sites-enabled/default ]]; then
    rm /etc/nginx/sites-enabled/default
fi
cat "${NMCT_HOME}/resources/conf/nginx" | envsubst '${NMCT_HOME}' > /etc/nginx/sites-available/nmct-box
ln -s /etc/nginx/sites-available/nmct-box /etc/nginx/sites-enabled/nmct-box
systemctl restart nginx




