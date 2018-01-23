# Adafruit NeoPixel library port to the rpi_ws281x library.
# Author: Tony DiCola (tony@tonydicola.com), Jeremy Garff (jer@jers.net)
import atexit
# https://raspberrytips.nl/neopixel-ws2811-raspberry-pi/
import functools
import logging
import queue
import threading
import time
from enum import Enum
from traceback import print_exception

import _rpi_ws281x as ws
import os
from matplotlib import colors

log = logging.getLogger(__name__)


class Color:
    def __init__(self, red=0, green=0, blue=0, name='Color'):
        self.red = self.r = red
        self.green = self.g = green
        self.blue = self.b = blue
        self.name = name

    """
    Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """

    def to_int(self):
        return (self.red << 16) | (self.green << 8) | self.blue

    __int__ = __index__ = to_int

    @classmethod
    def from_int(cls, value):
        r = value >> 16
        g = (value >> 8) & 0xff
        b = value & 0xff
        return cls(r, g, b)

    def to_tuple(self):
        return self.red, self.green, self.blue

    def __str__(self):
        return "Color({r}, {g}, {b})".format(r=self.red, g=self.green, b=self.blue)

    __repr__ = __str__

    def to_hex(self):
        return "{:0=6x}".format(self.to_int())

    __hex__ = to_hex

    @property
    def html(self):
        return "#{}".format(self.to_hex())

    @classmethod
    def by_name(cls, value):
        return cls(*[round(x * 255) for x in colors.hex2color(colors.CSS4_COLORS[value])])


CSS4_COLORS = {n: Color(*[round(x * 255) for x in colors.hex2color(v)])
               for n, v in colors.CSS4_COLORS.items()}
LETTER_COLORS = {n: Color(*[round(x * 255) for x in colors.hex2color(v)])
                 for n, v in colors.CSS4_COLORS.items()}

Palette = Enum("Palette", dict(list(CSS4_COLORS.items())))

for n, v in colors.CSS4_COLORS.items():
    setattr(Color, n, Color(*[round(x * 255) for x in colors.hex2color(v)]))

OFF = Color()

_animations = []


def animation(func):
    _animations.append(func)
    return func


class _LedArray(object):
    """Wrapper class which makes a SWIG LED color data array look and feel like
    a Python list of integers.
    """

    def __init__(self, channel, size):
        self.size = size
        self.channel = channel

    def __getitem__(self, pos):
        """Return the 24-bit RGB color value at the provided position or slice
        of positions.
        """
        # Handle if a slice of positions are passed in by grabbing all the values
        # and returning them in a list.
        if isinstance(pos, slice):
            return [Color.from_int(ws.ws2811_led_get(self.channel, n)) for n in range(pos.indices(self.size))]
        # Else assume the passed in value is a number to the position.
        else:
            return Color.from_int(ws.ws2811_led_get(self.channel, pos))

    def __setitem__(self, pos, value):
        """Set the 24-bit RGB color value at the provided position or slice of
        positions.
        """
        # Handle if a slice of positions are passed in by setting the appropriate
        # LED data values to the provided values.
        if isinstance(pos, slice):
            index = 0
            for n in range(pos.indices(self.size)):
                ws.ws2811_led_set(self.channel, n, int(value[index]))
                index += 1
        # Else assume the passed in value is a number to the position.
        else:
            return ws.ws2811_led_set(self.channel, pos, int(value))


_ws821x_lock = threading.RLock()


class PixelStrip(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, num, pin, freq_hz=800000, dma=5, invert=False, brightness=128, channel=0, gamma=None):
        """Class to represent a SK6812/WS281x LED display.  Num should be the
        number of pixels in the display, and pin should be the GPIO pin connected
        to the display signal line (must be a PWM pin like 18!).  Optional
        parameters are freq, the frequency of the display signal in hertz (default
        800khz), dma, the DMA channel to use (default 5), invert, a boolean
        specifying if the signal line should be inverted (default False), and
        channel, the PWM channel to use (defaults to 0).
        """

        if gamma is None:
            gamma = list(range(256))

        self._gamma = gamma

        # Keep track of successful init so we don't call ws2811_fini unecessarily
        self._init_successful = False

        # Create ws2811_t structure and fill in parameters.
        self._leds = ws.new_ws2811_t()

        # Initialize the channels to zero
        for channum in range(2):
            chan = ws.ws2811_channel_get(self._leds, channum)
            ws.ws2811_channel_t_count_set(chan, 0)
            ws.ws2811_channel_t_gpionum_set(chan, 0)
            ws.ws2811_channel_t_invert_set(chan, 0)
            ws.ws2811_channel_t_brightness_set(chan, 0)

        # Initialize the channel in use
        self._channel = ws.ws2811_channel_get(self._leds, channel)
        # ws.ws2811_channel_t_gamma_set(self._channel, self._gamma)
        ws.ws2811_channel_t_count_set(self._channel, num)
        ws.ws2811_channel_t_gpionum_set(self._channel, pin)
        ws.ws2811_channel_t_invert_set(self._channel, 0 if not invert else 1)
        ws.ws2811_channel_t_brightness_set(self._channel, brightness)
        ws.ws2811_channel_t_strip_type_set(self._channel, ws.WS2811_STRIP_GRB)

        # Initialize the controller
        ws.ws2811_t_freq_set(self._leds, freq_hz)
        ws.ws2811_t_dmanum_set(self._leds, dma)

        # Grab the led data array.
        self._led_data = _LedArray(self._channel, num)

        # Substitute for __del__, traps an exit condition and cleans up properly
        atexit.register(self._cleanup)

    def __del__(self):
        # Required because Python will complain about memory leaks
        # However there's no guarantee that "ws" will even be set
        # when the __del__ method for this class is reached.
        if ws is not None:
            self._cleanup()

    def _cleanup(self):
        # Clean up memory used by the library when not needed anymore.
        with _ws821x_lock:
            if self._leds is not None and self._init_successful:
                # ws.ws2811_fini(self._leds)
                #
                ws.delete_ws2811_t(self._leds)
                self._leds = None
                self._channel = None
                # Note that ws2811_fini will free the memory used by led_data internally.

    def set_gamma(self, gamma):
        with _ws821x_lock:
            if type(gamma) is list and len(gamma) == 256:
                self._gamma = gamma
                ws.ws2811_channel_t_gamma_set(self._channel, self._gamma)

    def begin(self):
        """Initialize library, must be called once before other functions are
        called.
        """
        with _ws821x_lock:
            resp = ws.ws2811_init(self._leds)
            if resp != 0:
                str_resp = ws.ws2811_get_return_t_str(resp)
                raise RuntimeError('ws2811_init failed with code {0} ({1})'.format(resp, str_resp))

            self._init_successful = True

    def show(self, t=0.0):
        """Update the display with the data from the LED buffer."""
        with _ws821x_lock:
            resp = ws.ws2811_render(self._leds)
            if resp != 0:
                str_resp = ws.ws2811_get_return_t_str(resp)
                raise RuntimeError('ws2811_render failed with code {0} ({1})'.format(resp, str_resp))
            time.sleep(t)

    def set_pixel_color(self, n, color):
        """Set LED at position n to the provided 24-bit color value (in RGB order).
        """
        with _ws821x_lock:
            self._led_data[n] = color

    def set_pixel_rgb(self, n, red, green, blue):
        """Set LED at position n to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        """
        self.set_pixel_color(n, Color(red, green, blue))

    def get_brightness(self):
        with _ws821x_lock:
            return ws.ws2811_channel_t_brightness_get(self._channel)

    def set_brightness(self, brightness):
        """Scale each LED in the buffer by the provided brightness.  A brightness
        of 0 is the darkest and 255 is the brightest.
        """
        with _ws821x_lock:
            ws.ws2811_channel_t_brightness_set(self._channel, brightness)

    def get_pixels(self):
        """Return an object which allows access to the LED display data as if
        it were a sequence of 24-bit RGB values.
        """
        return self._led_data

    def pixel_count(self):
        """Return the number of pixels in the display."""
        with _ws821x_lock:
            return ws.ws2811_channel_t_count_get(self._channel)

    __len__ = pixel_count

    def __iter__(self):
        return iter(range(len(self)))

    def __reversed__(self):
        return reversed(list(iter(self)))

    def get_pixel_color(self, n):
        """Get the 24-bit RGB color value for the LED at position n."""
        return self._led_data[n]

    def get_pixel_rgb(self, n):
        return self.get_pixel_color(n).to_tuple()


class PixelRing(PixelStrip):
    @animation
    def clear(self, *args, **kwargs):
        for led in self:
            self.set_pixel_color(led, OFF)
            self.show()

    sleep = PixelStrip.show

    @animation
    def loop(self, color: Color, *, speed=20, iterations=3):
        """Loop a single LED around the ring"""
        for i in range(iterations):
            for led in self:
                self.set_pixel_color(led, color)
                self.sleep(1 / speed)
                self.set_pixel_color(led, OFF)
                self.show()

    @animation
    def fill(self, color: Color, *args, speed=20):
        """Light all LEDs one by one"""
        for led in self:
            self.set_pixel_color(led, color)
            self.show()
            time.sleep(1 / speed)

    @animation
    def unfill(self, color: Color, *args, speed=20):
        """Loop a single LED around the ring"""
        for led in self:
            self.set_pixel_color(led, color)
        self.show()
        for led in reversed(self):
            self.set_pixel_color(led, OFF)
            self.show()
            time.sleep(1 / speed)

    @animation
    def theater_chase(self, color, *args, speed=20, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, len(self), 3):
                    self.set_pixel_color(i + q, color)
                    self.show()
                time.sleep(1 / speed)
                for i in range(0, len(self), 3):
                    self.set_pixel_color(i + q, OFF)
        self.clear()

    @staticmethod
    def _generate_rainbow(pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    @animation
    def rainbow(self, *args, speed=20):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for led in self:
            self.set_pixel_color(led, self._generate_rainbow((int(led * 256 / len(self))) & 255))
            self.show()
            time.sleep(1 / speed)

    @animation
    def rainbow_chase(self, *args, speed=20):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, len(self), 3):
                    self.set_pixel_color(i + q, self._generate_rainbow((i + j) % 255))
                    self.show()
                time.sleep(1 / speed)
                for i in range(0, len(self), 3):
                    self.set_pixel_color(i + q, OFF)


class NeoPixelThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="NeoPixelThread")
        self._queue = queue.Queue()
        self._ring = None
        if os.geteuid() == 0:
            self._ring = PixelRing(24, 12)
            self._ring.begin()

    def run(self):
        while True:
            try:
                funct = self._queue.get()
                if funct is None:
                    break
                funct()
            except Exception as ex:
                print_exception(ex, ex, ex.__traceback__)

    def queue_animation(self, ani, *args, **kwargs):
        if args is None:
            args = []
        if os.geteuid() == 0:
            self._queue.put(functools.partial(getattr(self._ring, ani), *args, **kwargs))
        else:
            msg = "No root, no ring!"
            log.error(msg)
            raise OSError(msg)

    @staticmethod
    def list_animations():
        return set(_animations)


if __name__ == "__main__":
    ring = PixelRing(24, 12)
    ring.begin()
    print("loop")
    ring.loop(Palette.RED)
    time.sleep(1)
    print("fill")
    ring.fill(Palette.GREEN)
    time.sleep(1)
    print("fill off")
    ring.fill(Palette.BLACK)
    time.sleep(1)
    print("unfill")
    ring.unfill(Palette.GREEN)
    time.sleep(1)
    print("rainbow chase")
    ring.rainbow_chase()
    time.sleep(1)
    print("theater chase")
    ring.theater_chase(Palette.BLUE)
    time.sleep(1)
    print("rainbow")
    ring.rainbow()
    time.sleep(1)
    print("clear")
    ring.clear()
    for name, col in dict(Palette).items():
        print("{}: {}".format(name, col))
        for led in ring:
            ring.set_pixel_color(led, col)
            ring.show()
            time.sleep(0.01)
            # ring.set_pixel_color(led, Color(0, 0, 0))
            # ring.show()
    for led in ring:
        ring.set_pixel_color(led, Palette.BLACK)
        ring.show()
