from collections import namedtuple
from time import sleep

import smbus
import math

# adxl address 0x53
# select the correct i2c bus for this revision of Raspberry Pi
revision = ([l[12:-1] for l in open('/proc/cpuinfo', 'r').readlines() if l[:8] == "Revision"] + ['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

# ADXL345 constants
EARTH_GRAVITY_MS2 = 9.80665
SCALE_MULTIPLIER = 0.004

DATA_FORMAT = 0x31
BW_RATE = 0x2C
POWER_CTL = 0x2D

BW_RATE_1600HZ = 0x0F
BW_RATE_800HZ = 0x0E
BW_RATE_400HZ = 0x0D
BW_RATE_200HZ = 0x0C
BW_RATE_100HZ = 0x0B
BW_RATE_50HZ = 0x0A
BW_RATE_25HZ = 0x09

RANGE_2G = 0x00
RANGE_4G = 0x01
RANGE_8G = 0x02
RANGE_16G = 0x03

MEASURE = 0x08
AXES_DATA = 0x32

Acceleration = namedtuple("Acceleration", "x y z")
Tilt = namedtuple("Tilt", "roll pitch")


class ADXL345:
    address = None

    def __init__(self, address=0x53):
        self.address = address
        self.set_bandwidth(BW_RATE_100HZ)
        self.set_range(RANGE_2G)
        self.enable()

    def enable(self):
        bus.write_byte_data(self.address, POWER_CTL, MEASURE)

    def set_bandwidth(self, rate_flag):
        bus.write_byte_data(self.address, BW_RATE, rate_flag)

    # set the measurement range for 10-bit readings
    def set_range(self, range_flag):
        value = bus.read_byte_data(self.address, DATA_FORMAT)

        value &= ~0x0F
        value |= range_flag
        value |= 0x08

        bus.write_byte_data(self.address, DATA_FORMAT, value)

    # returns the current reading from the sensor for each axis
    #
    # parameter gforce:
    #    False (default): result is returned in m/s^2
    #    True           : result is returned in gs
    def measure(self, gforce=False):
        data = bus.read_i2c_block_data(self.address, AXES_DATA, 6)
        x, y, z = [
            round(
                SCALE_MULTIPLIER *
                (1 if gforce else EARTH_GRAVITY_MS2) *
                int.from_bytes([lsb, msb], 'little', signed=True)
                , 4)
            for lsb, msb in zip(data[0::2], data[1::2])
        ]
        return Acceleration(x, y, z)

    def tilt(self):
        x, y, z = self.measure()
        roll = math.atan2(y, math.sqrt(x * x + z * z)) * 180 / math.pi
        pitch = math.atan2(x, math.sqrt(y * y + z * z)) * 180 / math.pi
        return Tilt(roll, pitch)


if __name__ == "__main__":
    # if run directly we'll just create an instance of the class and output
    # the current readings
    adxl345 = ADXL345()
    while True:
        acc = adxl345.measure(True)
        print("ADXL345 on address 0x{:x}: {}".format(adxl345.address, acc))
        sleep(1)
