#!/usr/bin/env python3
# Copyright 2018 Howest/NMCT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Internet check and IP configuration with LCD display"""

import logging
import signal

import aiy.voicehat
import sys

import time

import nmct.box
import nmct.snowboy
import nmct.watson

logging.basicConfig()
logging.getLogger().setLevel(logging.WARN)


def ipconfig():
    lcd = nmct.box.get_display()
    button = aiy.voicehat.get_button()
    delay = 3

    def shutdown(*args):
        lcd.clear()
        time.sleep(1)
        try:
            nmct.box.stop()
            sys.exit(0)
        except Exception as ex:
            pass

    button.on_press(shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        lcd.write_line("NMCT-Box".center(16), 1)
        if nmct.box.test_internet():
            lcd.write_line("Internet OK  :-)", 2)
        else:
            lcd.write_line("No Internet  :-(", 2)
        time.sleep(delay)

        interfaces = nmct.box.get_ipconfig()
        for iface, addresses in interfaces.items():
            lcd.write_line("{}: ".format(iface).ljust(16), 1)
            for addr in addresses:
                lcd.write_line(addr.rjust(16), 2)
                time.sleep(delay)

        lcd.write_line("hostname:".ljust(16), 1)
        lcd.write_line(nmct.box.get_hostname().rjust(16), 2)
        time.sleep(delay)


if __name__ == '__main__':
    time.sleep(20)      # make sure we are fully booted and online
    ipconfig()
