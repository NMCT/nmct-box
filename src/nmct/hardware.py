from nmct.drivers.adxl345 import ADXL345
from nmct.drivers.lcd import LCDisplay
from nmct.drivers.neopixel import NeoPixelThread
from nmct.drivers.onewire import Thermometer

_accelerometer = None
_temp_probe = None
_display = None
_pixelring = None


def measure_temperature():
    return get_thermometer().measure()


def measure_acceleration():
    acc = get_accelerometer()
    return acc.measure()


def get_thermometer():
    return Thermometer("28-0417b27173ff")  # TODO: autodetect ID


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
