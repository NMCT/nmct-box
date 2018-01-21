#!/usr/bin/env bash
#
# Install dependencies and NMCT Box services


set -o errexit

[[ -z ${NMCT_HOME} ]] && export NMCT_HOME="$(dirname "${PWD}")"
echo "Installing to ${NMCT_HOME}"
readonly PYENV="${NMCT_HOME}/env/bin/python"

# dependencies
readonly APT_PACKAGES="python3-dev python3-venv swig libatlas-base-dev scons libffi-dev portaudio19-dev python3-pyaudio sox libssl-dev nginx python3-notebook"
readonly NPM_PACKAGES=


source ./nmct-box.sh

#
# Command line options
#
for i in $*; do
    case ${i} in
    --nmct-only)
        install_nmct_box
        install_services
        install_shortcuts
        exit $?
        ;;
    esac
done

install_packages
create_venv
install_aiy_voicekit
install_snowboy
install_neopixel
install_nmct_box
install_npm_packages configurable-http-proxy
install_services
install_shortcuts

printf "Done. If you just installed the AIY drivers for the first time, reboot and run '%s/aiy-voicekit/checkpoints/check_audio.py'\n" ${NMCT_HOME}
