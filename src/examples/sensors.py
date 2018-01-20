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

"""A demo of Snowboy hotword detection."""

import logging

import nmct.box
import nmct.snowboy
import nmct.watson

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def sensor_demo():
    print(dict(nmct.box.measure_acceleration()))


if __name__ == '__main__':
    sensor_demo()
