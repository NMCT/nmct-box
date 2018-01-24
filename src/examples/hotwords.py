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

"""A demo of Snowboy hotword detection."""

import atexit
import logging
import time

import aiy.audio
import aiy.voicehat
import sys

import nmct.box
import nmct.box
import nmct.snowboy
import nmct.watson

logging.basicConfig()
logging.getLogger().setLevel(logging.WARN)


def hotword_demo():
    led = aiy.voicehat.get_led()
    detector = nmct.snowboy.get_detector()

    print("Hotwords:")
    for hotword in nmct.snowboy.builtin_hotwords():
        print(hotword.name)
        detector.add_hotword(hotword)

    button = aiy.voicehat.get_button()

    def shutdown(*args):
        try:
            aiy.audio.get_recorder().stop()
            nmct.box.stop()
            sys.exit(0)
        except Exception as ex:
            pass

    button.on_press(shutdown)

    aiy.audio.get_recorder().start()

    while True:
        print('Waiting for hotword...')
        word = detector.wait_for_hotword()
        led.set_state(led.DECAY)
        print('Detected: {}...'.format(word.name))
        nmct.box.play_sound('dong')
        time.sleep(1)
        led.set_state(led.OFF)


if __name__ == '__main__':
    hotword_demo()
