#!/usr/bin/env bash
if [[ -z "${NMCT_HOME}" ]]; then
    readonly NMCT_HOME="/opt/nmct-box"
fi;

source "${NMCT_HOME}/env/bin/activate"
pushd "${NMCT_HOME}/src/examples"
python teammeeting_demo.py
popd
