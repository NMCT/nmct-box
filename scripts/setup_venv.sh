#!/bin/bash
if [ $(id -u) -ne 0 ]; then
  printf "Script must be run as root! Try 'sudo %s'\n" $0 >&2
  exit 1
fi

echo "This script is untested, good luck!:)"    # FIXME

readonly nmct_home="${PWD}/.."
readonly venv="${nmct_home}/env"
readonly temp="/tmp/nmct"
readonly packages="python3-dev python3-venv swig libatlas-base-dev scons"

apt update -y && apt install -y ${packages}

python3 -m venv ${venv}
${venv}/bin/python -m pip install --upgrade pip setuptools wheel distutils
source ${venv}/bin/activate


dir=${temp}/aiy
git clone https://github.com/google/aiyprojects-raspbian.git ${dir}
pushd ${dir}
git checkout aiyprojects
cd src
${venv}/bin/python setup.py install
popd


dir=${temp}/snowboy
git clone https://github.com/Kitt-AI/snowboy.git ${dir}
pushd ${dir}
${venv}/bin/python setup.py build install
popd


dir=${temp}/rpi-ws821x
git clone https://github.com/jgarff/rpi_ws281x.git ${dir}
pushd ${dir}
scons
pushd ${dir}/python
${venv}/bin/python setup.py build install

pushd "${nmct_home}/src"
python setup.py install

deactivate

