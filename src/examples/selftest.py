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

"""A demo of the NMCT Box."""

import atexit
import logging
import sys
import time

import aiy.audio
import aiy.voicehat

import nmct.box
import nmct.snowboy
import nmct.watson
from nmct.drivers.neopixel import Palette, Color

logging.basicConfig()
logging.getLogger().setLevel(logging.WARN)


def nmct_box_demo():
    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()

    ring = nmct.box.get_pixel_ring()
    lcd = nmct.box.get_display()
    acc = nmct.box.get_accelerometer()

    aiy.audio.get_tts_volume()
    aiy.audio.get_recorder().start()
    atexit.register(aiy.audio.get_recorder().stop)

    ring.queue_animation('loop', color=Palette.white, iterations=3)

    lcd.write_line("--- NMCT Box ---", 0)
    lcd.write_line("testing, 1, 2, 3", 1)

    led.set_state(aiy.voicehat.LED.ON)
    button.wait_for_press()
    led.set_state(aiy.voicehat.LED.OFF)

    aiy.audio.get_player()


if __name__ == '__main__':
    nmct_box_demo()
