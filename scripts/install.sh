#!/bin/bash
if [[ $EUID -ne 0 ]]; then
  printf "Script must be run as root! Try 'sudo %s'\n" $0 >&2
  exit 1
fi

echo "This script is untested, good luck!:)"    # FIXME

export NMCT_HOME="$(dirname "${PWD}")"
readonly venv="${NMCT_HOME}/env"
readonly temp="/tmp/nmct"
readonly APT_PKG="python3-dev python3-venv swig libatlas-base-dev scons libffi-dev portaudio19-dev \
python3-pyaudio sox libssl-dev nginx ufw python3-notebook npm"
readonly NPM_PKG="configurable-http-proxy"

# install APT packages
apt update -y && apt install -y ${APT_PKG}

# install NPM packages
npm install -g ${NPM_PKG}

# TODO: py packages thru pip/requirements.txt

# create venv
python3 -m venv ${venv}
${venv}/bin/python -m pip install --upgrade pip setuptools wheel distutils
source ${venv}/bin/activate

# pull & install AIY drivers
dir=${temp}/aiy
git clone https://github.com/google/aiyprojects-raspbian.git ${dir}
pushd ${dir}
git checkout aiyprojects
cd src
# TODO execute shell scripts
${venv}/bin/python setup.py install
popd

# pull & install Snowboy
dir=${temp}/snowboy
git clone https://github.com/Kitt-AI/snowboy.git ${dir}
pushd ${dir}
${venv}/bin/python setup.py build install
popd

# pull & install NeoPixel driver
dir=${temp}/rpi-ws821x
git clone https://github.com/jgarff/rpi_ws281x.git ${dir}
pushd ${dir}
scons
pushd ${dir}/python
${venv}/bin/python setup.py build install

# install our package(s)
pushd "${NMCT_HOME}/src"
python setup.py install

# install services
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

deactivate


