#!/usr/bin/env python3
# Copyright 2017 Google Inc.
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

"""A demo of the Google CloudSpeech recognizer."""
import logging
import time

import aiy.audio
import aiy.voicehat
import nmct.watson
import nmct.snowboy
import nmct.sensors

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def main():
    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()

    print(nmct.sensors.get_temperature())

    detector = nmct.snowboy.get_detector()
    detector.add_hotword("NMCT.seb.pmdl")
    detector.add_hotword("NMCT.chris.pmdl")
    detector.add_hotword("NMCT.dieter.pmdl")

    recognizer = nmct.watson.get_recognizer()
    conversation = nmct.watson.get_conversation("9de1dde4-e3a6-406b-9913-82e5ce74f64c")

    aiy.audio.get_recorder().start()

    def perform_action(action):
        if "lights_on" in action:
            led.set_state(aiy.voicehat.LED.ON)
        elif "lights_off" in action:
            led.set_state(aiy.voicehat.LED.OFF)

    while True:
        # button.wait_for_press()
        # print('Waiting for hotword...')
        # word = detector.wait_for_hotword()
        # print('Detected: {}...'.format(word.name))
        text = "Hi"
        while not conversation.finished:
            if not text:
                print('Sorry, I did not hear you.')
            else:
                print('You said "', text, '"')
                response = conversation.message(text)
                print(response)
                if "text" in response:
                    # aiy.audio.say(response["text"][0])
                    nmct.watson.say(response["text"][0])
                if "action" in response:
                    perform_action(response["action"])
            text = recognizer.recognize()


if __name__ == '__main__':
    main()
