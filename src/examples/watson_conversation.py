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

"""A demo of IBM Watson Speech-to-Text, Conversation and Text-to-Speech."""

import logging

import aiy.audio
import aiy.voicehat
import nmct.box
import nmct.snowboy
import nmct.watson

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def conversation_demo():
    led = aiy.voicehat.get_led()

    # print(nmct.sensors.get_temperature())

    recognizer = nmct.watson.get_recognizer()
    conversation = nmct.watson.get_conversation("9de1dde4-e3a6-406b-9913-82e5ce74f64c")

    recorder = aiy.audio.get_recorder()
    recorder.start()

    def perform_action(action):
        if "lights_on" in action:
            led.set_state(aiy.voicehat.LED.ON)
        elif "lights_off" in action:
            led.set_state(aiy.voicehat.LED.OFF)

    text = "Hi"
    while not conversation.finished:
        if not text:
            print('Sorry, I did not hear you.')
        else:
            print('You said "', text, '"')
            intents, entities, output = conversation.message(text)
            print(intents, entities)
            if "text" in output:
                print(output["text"])
                # For some reason, sometimes Watson returns an empty text as first element
                for text in output["text"]:
                    if len(text) > 0:
                        # aiy.audio.say(text)
                        nmct.watson.say(text)
                        break
            if "action" in output:
                perform_action(output["action"])
            if "goodbyes" in intents:
                print('finish')
                recorder.stop()
                conversation.finish()
            else:
                text = recognizer.recognize()


if __name__ == '__main__':
    conversation_demo()
