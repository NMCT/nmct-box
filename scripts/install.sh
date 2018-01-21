#!/usr/bin/env bash
#
# Install dependencies and NMCT Box services


set -o errexit


source "$(dirname "${BASH_SOURCE}")/nmct-box.sh"


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
