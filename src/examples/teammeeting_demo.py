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

import nmct.hardware
import nmct.snowboy
import nmct.watson
from nmct.drivers.neopixel import COLORS

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def teammeeting_demo():
    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()

    ring = nmct.box.get_pixel_ring()
    lcd = nmct.box.get_display()
    acc = nmct.box.get_accelerometer()
    temp = nmct.box.get_thermometer()

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
    conversation = nmct.watson.get_conversation("9de1dde4-e3a6-406b-9913-82e5ce74f64c")

    aiy.audio.get_tts_volume()
    aiy.audio.get_recorder().start()
    atexit.register(aiy.audio.get_recorder().stop)

    def script():
        lcd.write("--- NMCT Box ---")
        ring.queue_effect("fill", COLORS["ORANGE"])
        ring.queue_effect("sleep", 0.5)
        ring.queue_effect("fill", COLORS["BLACK"])
        aiy.audio.say("Hi. I'm the NMCT box of doom and hell fire and I'd like to introduce you to some of my friends.")
        aiy.audio.say("Press my big, round button to get started.")
        button.wait_for_press()

        allison.say("I'm Allison. I can tell you about my environment. Press the button to measure my acceleration.")
        button.wait_for_press()
        allison.say("My acceleration is {x} G on the X-axis, {y} on y and {z} on the z-axis"
                    .format(**dict(acc.measure(gforce=True)._asdict())))
        time.sleep(1)

        michael.say("Hi, I'm Michael and I'm a doctor. Please insert the probe so I can read your temperature.")
        ring.queue_effect("rainbow")
        michael.say("Go ahead. Trust me. I'm a doctor. Press the button when it's in. ")
        lcd.write("Do it! Do it!")
        ring.queue_effect("clear")
        button.wait_for_press()
        michael.say("Your temperature measures {:.2f} degrees. I'd say that's cause for concern!"
                    .format(temp.measure()))
        ring.queue_effect("theater_chase", COLORS["RED"])
        ring.queue_effect("clear")

        time.sleep(1)
        aiy.audio.say("I can listen for hotwords too. Say the magic word...")
        lcd.write('Say "NMCT"!')
        led.set_state(led.BEACON)
        detector.wait_for_hotword()
        led.set_state(led.OFF)
        ring.queue_effect("theater_chase", COLORS["BLUE"])
        lcd.clear()
        ring.queue_effect("clear")
        lcd.write_line("--- NMCT Box ---", 0)

        aiy.audio.say(
            "Well done! Now meet some of my friends from all over the world. They can translate for you!")
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

        aiy.audio.say(
            "Now meet Kate from the UK. Ever since the accident, she imagines she's a car. "
            "You can ask her for lights or music, when you are done just tell her goodbye. ")

        def perform_action(action):
            if "lights_on" in action:
                ring.queue_effect("fill", COLORS["WHITE"])
            elif "lights_off" in action:
                ring.queue_effect("fill", COLORS["BLACK"])
            if "music_on" in action:
                if action["music_on"] == "jazz":
                    aiy.audio.get_player().play_wav("data/jazz.wav")
                elif action["music_on"] == "rock":
                    aiy.audio.get_player().play_wav("data/rock.wav")
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
                    kate.say(output["text"][0])
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
        ring.queue_effect("rainbow_chase", speed=200)
        ring.queue_effect("clear")
        aiy.audio.say("That was fun. I hope it was as good for you as it was for me. "
                      "See you around, if you need me, I'll be in my box!")
        aiy.audio.get_recorder().stop()

    script()
    sys.exit(0)


if __name__ == '__main__':
    teammeeting_demo()
