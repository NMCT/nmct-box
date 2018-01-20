#!/usr/bin/env bash
#
# Copy student html from dropbox to templates

# TODO: desktop shortcut to this script

if [[ -z "${NMCT_HOME}" ]]; then
    readonly NMCT_HOME"/opt/nmct-box-aiy"
fi;
readonly DROPBOX_UPLOADER="/home/pi/Dropbox-Uploader/dropbox_uploader.sh"

rm -f /home/pi/nmct_box/templates/student*.html
for file in student{1..25}.html; do
    echo ${file}
    ${DROPBOX_UPLOADER} download "${file}" "${NMCT_HOME}/src/web/templates"
done
