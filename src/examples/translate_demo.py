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

    recognizer = nmct.watson.get_recognizer()
    print(recognizer.list_models())

    translator = nmct.watson.get_translator()
    print(translator.list_models())
    translator.set_model('en-es-conversational')

    synthesizer = nmct.watson.get_synthesizer()
    print(synthesizer.list_voices())
    synthesizer.voice = 'es-LA_SofiaVoice'

    aiy.audio.get_recorder().start()

    while True:
        button.wait_for_press()
        led.set_state(aiy.voicehat.LED.ON)
        text = recognizer.recognize()
        led.set_state(aiy.voicehat.LED.OFF)

        if not text:
            print('Sorry, I did not hear you.')
        else:
            print('You said "', text, '"')
            response = translator.translate(text)
            if "translation" in response:
                translation = response["translation"]
                print(translation)
                audio = synthesizer.synthesize(translation)
                aiy.audio.get_player().play_bytes(audio, 16000)


if __name__ == '__main__':
    main()
