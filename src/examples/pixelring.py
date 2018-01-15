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

import nmct.hardware
from nmct.drivers.neopixel import COLORS

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def main():
    ring = nmct.hardware.get_pixel_ring()
    # ring.queue_effect("rainbow")
    # ring.queue_effect("clear")
    # time.sleep(1)
    yellow_ = COLORS["YELLOW"]
    ring.queue_effect("fill", yellow_)
    print(yellow_)
    time.sleep(2)
    ring.queue_effect("fill", COLORS["BLACK"])
    # ring.queue_effect("theater_chase", COLORS["BLUE"])
    # ring.queue_effect("clear")
    ring.join()  # FIXME


if __name__ == '__main__':
    main()
