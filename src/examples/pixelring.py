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

"""A demo of the NeoPixel LED ring"""

import logging
import time

from nmct import Palette

import nmct.box

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def pixelring_demo():
    ring = nmct.box.get_pixel_ring()
    ring.queue_animation("rainbow")
    ring.queue_animation("clear")
    time.sleep(1)
    yellow_ = Palette.yellow
    ring.queue_animation("fill", yellow_)
    print(yellow_)
    time.sleep(2)
    ring.queue_animation("fill", Palette.black)
    ring.queue_animation("theater_chase", Palette.blue)
    ring.queue_animation("clear")
    nmct.box.stop()


if __name__ == '__main__':
    pixelring_demo()
