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

    detector = nmct.snowboy.get_detector()
    detector.add_hotword("NMCT.seb.pmdl")
    detector.add_hotword("NMCT.chris.pmdl")
    detector.add_hotword("NMCT.chrisv2.pmdl")
    detector.add_hotword("NMCT.dieter.pmdl")

    recognizer = nmct.watson.get_recognizer()
    # print(recognizer.list_models())

    en_es = nmct.watson.get_translator()
    # print(en_es.list_models())
    en_es.set_model('en-es-conversational')
    en_de = nmct.watson.get_translator('en', 'de')

    allison = nmct.watson.get_synthesizer("en-US_AllisonVoice")
    # print(allison.list_voices())
    sofia = nmct.watson.get_synthesizer('es-LA_SofiaVoice')
    kate = nmct.watson.get_synthesizer('en-GB_KateVoice')
    michael = nmct.watson.get_synthesizer('en-US_MichaelVoice')
    dieter = nmct.watson.get_synthesizer('de-DE_DieterVoice')
    lisa = nmct.watson.get_synthesizer('en-US_LisaVoice')
    conversation = nmct.watson.get_conversation("9de1dde4-e3a6-406b-9913-82e5ce74f64c")

    aiy.audio.get_tts_volume()
    aiy.audio.get_recorder().start()
    atexit.register(aiy.audio.get_recorder().stop)

    def script():

        lcd.write("--- NMCT Box ---")
        ring.queue_animation("fill", Palette.orange)
        ring.queue_animation("sleep", 0.5)
        ring.queue_animation("fill", Palette.black)
        lisa.say("Hi. I'm the NMCT box of arbitrary code execution and I'd like you to meet some of my friends."
                 "Press my big, round button to get started.")
        led.set_state(aiy.voicehat.LED.ON)
        button.wait_for_press()
        led.set_state(aiy.voicehat.LED.OFF)

        allison.say("Hello, I'm Allison. I can tell you about my environment. Press the button to measure acceleration.")
        led.set_state(aiy.voicehat.LED.ON)
        button.wait_for_press()
        led.set_state(aiy.voicehat.LED.OFF)

        allison.say("My acceleration is {x} G on the X-axis, {y} on y and {z} on the z-axis"
                    .format(**dict(acc.measure(gforce=True)._asdict())))
        time.sleep(1)

        michael.say("Hi, I'm Michael and I'm a doctor. Please insert the probe so I can read your temperature.")
        ring.queue_animation("rainbow")
        michael.say("Go ahead. Trust me. I'm a doctor. Press the button when it's in. ")
        lcd.write("Do it! Do it!")
        ring.queue_animation("clear")
        button.wait_for_press()
        michael.say("Your temperature measures {:.2f} degrees. I'd say that's cause for concern!"
                    .format(nmct.box.measure_temperature()))
        ring.queue_animation("theater_chase", Palette.red)
        ring.queue_animation("clear")

        time.sleep(1)
        lisa.say("I can listen for hotwords too. Say the magic word...")
        lcd.write('Say "NMCT"!')
        led.set_state(led.BEACON)
        detector.wait_for_hotword()
        led.set_state(led.OFF)
        ring.queue_animation("theater_chase", Palette.blue)
        lcd.clear()
        ring.queue_animation("clear")
        lcd.write_line("--- NMCT Box ---", 0)

        lisa.say(
            "Well done! Now meet some of my friends from all over the world. They can translate for you! "
            "After they introduce themselves, wait for my button to light up and say something in English...")
        time.sleep(1)
        sofia.say("Hola! Me llamo Sofia y hablos espanol!")
        led.set_state(aiy.voicehat.LED.ON)
        text = recognizer.recognize()
        led.set_state(aiy.voicehat.LED.OFF)
        if not text:
            msg = 'Sorry, I did not hear you.'
            print(msg)
            aiy.audio.get_player().play_bytes(allison.synthesize(msg), 16000)
        else:
            print('You said: {}'.format(text))
            response = en_es.translate(text)
            if "translation" in response:
                translation = response["translation"]
                print("Translation: {}".format(translation))
                audio = sofia.synthesize(translation)
                aiy.audio.get_player().play_bytes(audio, 16000)

        time.sleep(1)
        dieter.say("AUFMACHEN!!! ehhh. Entschuldigung. Ich bin Dieter, und ich spreche Deutsch.")
        led.set_state(aiy.voicehat.LED.ON)
        text = recognizer.recognize()
        led.set_state(aiy.voicehat.LED.OFF)
        if not text:
            msg = 'Sorry, I did not hear you.'
            print(msg)
            aiy.audio.get_player().play_bytes(allison.synthesize(msg), 16000)
        else:
            print('You said: {}'.format(text))
            response = en_de.translate(text)
            if "translation" in response:
                translation = response["translation"]
                print("Translation: {}".format(translation))
                dieter.say(translation)
        time.sleep(1)
        lisa.say(
            "Now meet Kate from the UK. Ever since the accident, she imagines she's a car. "
            "You can ask her for lights or music, when you are done just tell her goodbye. ")

        def perform_action(action):
            if "lights_on" in action:
                ring.queue_animation("fill", Palette.white)
            elif "lights_off" in action:
                ring.queue_animation("fill", Palette.black)
            if "music_on" in action:
                if action["music_on"] == "jazz":
                    nmct.box.play_sound("jazz")
                elif action["music_on"] == "rock":
                    nmct.box.play_sound("rock")
                kate.say("That was nice. Anything else?")

        text = "Hi"
        while not conversation.finished:
            if not text:
                print('Sorry, I did not hear you.')
            else:
                print('You said "', text, '"')
                intents, entities, output = conversation.message(text)
                print(intents, entities, output)
                if "text" in output:
                    print(output["text"])
                    # For some reason, sometimes Watson returns an empty text as first element
                    for text in output["text"]:
                        if len(text) > 0:
                            # aiy.audio.say(text)
                            kate.say(text)
                            break
                if "action" in output:
                    perform_action(output["action"])
                if "goodbyes" in intents:
                    print('finish')
                    conversation.finish()
                else:
                    led.set_state(aiy.voicehat.LED.ON)
                    text = recognizer.recognize()
                    led.set_state(aiy.voicehat.LED.OFF)
        time.sleep(1)
        ring.queue_animation("rainbow_chase", speed=200)
        ring.queue_animation("clear")
        lisa.say("That was fun. I hope it was as good for you as it was for me. "
                 "See you around, if you need me, I'll be in my box... wink, wink!")
        aiy.audio.get_recorder().stop()
        nmct.box.stop()

    script()
    # sys.exit(0)


if __name__ == '__main__':
    nmct_box_demo()
