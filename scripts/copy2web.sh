#!/usr/bin/env bash
#
# Copy student html from dropbox to templates

# TODO: desktop shortcut to this script

[[ -z ${NMCT_HOME} ]] &&
readonly DROPBOX_UPLOADER="${NMCT_HOME}/scripts/dropbox_uploader.sh" ||
readonly DROPBOX_UPLOADER="${BASH_SOURCE}dropbox_uploader.sh"

rm -f /home/pi/nmct_box/templates/student*.html
for file in student{1..25}.html; do
    echo ${file}
    ${DROPBOX_UPLOADER} download "${file}" "${NMCT_HOME}/src/web/templates"
done
