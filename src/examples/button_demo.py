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

    player = aiy.audio.get_player()

    ring = nmct.box.get_pixel_ring()
    lcd = nmct.box.get_display()
    # kate = nmct.watson.get_synthesizer('en-GB_KateVoice')
    # lisa = nmct.watson.get_synthesizer('en-US_LisaVoice')
    # audio = lisa.synthesize("Hi! I'm the New Media and Communication Technology box, welcome to our info event!")
    #
    # with open('infodag.pcm', 'wb') as f:
    #     f.write(audio)

    with open('/home/nmct/infodag.pcm', 'rb') as f:
        audio = f.read()

    lcd.write_line("  Welkom op de  ", 1)
    lcd.write_line("infodag van NMCT", 0)

    while True:
        print("Waiting for press... ")
        button.wait_for_press()
        led.set_state(1)
        ring.queue_animation("rainbow")
        player.play_bytes(audio, 16000)
        # kate.say("Hi! I'm the New Media and Communication Technology box, welcome to our info event!")
        led.set_state(0)

if __name__ == '__main__':
    nmct_box_demo()
