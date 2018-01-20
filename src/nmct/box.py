import socket
from pathlib import Path
import os

import aiy.audio
import netifaces

from nmct import settings
from nmct.drivers.adxl345 import ADXL345
from nmct.drivers.lcd import LCDisplay
from nmct.drivers.neopixel import NeoPixelThread
from nmct.drivers.onewire import Thermometer

_audio_path = Path(os.path.join(os.path.dirname(settings.RESOURCE_PATH), 'audio'))
_accelerometer = None
_temp_probe = None
_display = None
_pixelring = None


def measure_temperature():
    return get_thermometer().measure()


def measure_acceleration():
    acc = get_accelerometer()
    return acc.measure()


def get_thermometer(w1id="28-0417b27173ff"):
    return Thermometer(w1id)  # TODO: autodetect ID?


def get_accelerometer():
    global _accelerometer
    if _accelerometer is None:
        _accelerometer = ADXL345()
    return _accelerometer


def get_display():
    global _display
    if _display is None:
        _display = LCDisplay(26, 13)
    return _display


def get_pixel_ring():
    global _pixelring
    if _pixelring is None:
        _pixelring = NeoPixelThread()
        _pixelring.start()
    return _pixelring


def play_sound(name):
    aiy.audio.get_player().play_wav(
        _audio_path.absolute().joinpath(os.path.join('{}.wav'.format(name))).absolute().as_posix())


def list_sounds():
    return [f.stem for f in _audio_path.glob('*.wav')]


def test_internet():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('www.google.com', 80))
        s.close()
        return True
    except OSError:
        return False


def get_ipconfig():
    return {iface: [i['addr'] for i in
                    netifaces.ifaddresses(iface).setdefault(netifaces.AF_INET, [{'addr': 'No IP addr'}])]
            for iface in netifaces.interfaces() if iface != 'lo'}


def get_hostname():
    return socket.gethostname()
