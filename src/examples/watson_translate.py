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

"""A demo of IBM Watson Speech-to-Text, Language Translator and Text-to-Speech."""

import atexit
import logging

import aiy.audio
import aiy.voicehat

import nmct.box
import nmct.snowboy
import nmct.watson

logging.basicConfig()
logging.getLogger().setLevel(logging.WARN)


def translate_demo():
    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()

    recognizer = nmct.watson.get_recognizer()
    print("Available recognition models: \n" + "\n".join(recognizer.list_models()))

    translator = nmct.watson.get_translator()
    print("Available translation models: \n" + "\n".join(model[0] for model in translator.list_models()))
    translator.set_model('en-es-conversational')

    english = nmct.watson.get_synthesizer()
    print("Available voices and languages for text to speech:\n" + "\n".join(english.list_voices()))

    spanish = nmct.watson.get_synthesizer('es-LA_SofiaVoice')

    aiy.audio.get_recorder().start()

    while True:
        print("Press the button, then speak! Say 'stop' to end the loop.")
        button.wait_for_press()
        led.set_state(aiy.voicehat.LED.ON)
        text = recognizer.recognize()
        led.set_state(aiy.voicehat.LED.OFF)
        if not text:
            msg = 'Sorry, I did not hear you.'
            print(msg)
            aiy.audio.get_player().play_bytes(english.synthesize(msg), 16000)
        else:
            print('You said: {}'.format(text))
            if text.strip() == "stop":
                break
            response = translator.translate(text)
            if "translation" in response:
                translation = response["translation"]
                print("Translation: {}".format(translation))
                audio = spanish.synthesize(translation)
                aiy.audio.get_player().play_bytes(audio, 16000)

    aiy.audio.get_recorder().stop()
    nmct.box.stop()


if __name__ == '__main__':
    translate_demo()
