import time
from threading import RLock

import RPi.GPIO as GPIO


class I2C:
    def __init__(self, sda, scl, adres):
        self.sda = sda
        self.scl = scl
        self.__setup()
        self.__start_address(adres)

    def __setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sda, GPIO.OUT)
        GPIO.setup(self.scl, GPIO.OUT)

    def __start_address(self, address):
        self.__start()
        self.write(address)

    def __start(self):
        GPIO.output(self.sda, True)
        GPIO.output(self.scl, GPIO.HIGH)
        time.sleep(0.01)

        GPIO.output(self.sda, GPIO.LOW)
        time.sleep(0.01)

        GPIO.output(self.scl, GPIO.LOW)
        time.sleep(0.01)

    def __write_bit(self, bit):
        GPIO.output(self.sda, bit)
        GPIO.output(self.scl, GPIO.LOW)
        GPIO.output(self.scl, GPIO.HIGH)
        GPIO.output(self.scl, GPIO.LOW)

    def write(self, byte):
        for i in range(7, -1, -1):
            if (byte & (1 << i)) > 0:
                self.__write_bit(True)
            else:
                self.__write_bit(False)
        self.__ack()

    def __ack(self):
        self.__write_bit(False)


class LCDisplay:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    # display werkt goed zonder levelshifter maar moet een voeding krijgen van 5 Volt.
    I2C_ADDR = 0x4E  # 0x7e  # I2C device address  0x3f   #adres in de pi dus nog 1 naar links shiften
    LCD_WIDTH = 16  # Maximum characters per line

    # Define some device constants
    LCD_CHR = 1  # Mode - Sending data
    LCD_CMD = 0  # Mode - Sending command

    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
    LCD_SCROLL = 0x18
    LCD_CURSOR_MOVE = 0x10

    # Timing constants
    E_PULSE = 0.005
    E_DELAY = 0.001

    ENABLE = 0x4

    LCD_BACKLIGHT = 0x08  # On

    # LCD_BACKLIGHT = 0x00  # Off

    def __init__(self, sda, scl):
        self._driver = I2C(sda, scl, LCDisplay.I2C_ADDR)
        self._lock = RLock()
        self.__lcd_init()

    def __lcd_init(self):
        # Initialise display
        self.__lcd_byte(0x33, LCDisplay.LCD_CMD)  # 110011 Initialise
        self.__lcd_byte(0x32, LCDisplay.LCD_CMD)  # 110010 Initialise
        self.__lcd_byte(0x28, LCDisplay.LCD_CMD)  # 101000 Data length, number of lines, font size
        self.__lcd_byte(0x0C, LCDisplay.LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
        self.__lcd_byte(0x01, LCDisplay.LCD_CMD)  # 000001 Clear display
        time.sleep(LCDisplay.E_DELAY)
        self.__lcd_byte(LCDisplay.LCD_LINE_1, LCDisplay.LCD_CMD)  # Move to start

    def __lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command
        bits_high = mode | (bits & 0xF0) | LCDisplay.LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | LCDisplay.LCD_BACKLIGHT
        # High bits
        self._driver.write(bits_high)
        self.__lcd_toggle_enable(bits_high)
        # Low bits
        self._driver.write(bits_low)
        self.__lcd_toggle_enable(bits_low)

    def __lcd_toggle_enable(self, bits):
        # Toggle enable
        time.sleep(LCDisplay.E_DELAY)
        self._driver.write(bits | LCDisplay.ENABLE)
        time.sleep(LCDisplay.E_PULSE)
        self._driver.write(bits & ~LCDisplay.ENABLE)
        time.sleep(LCDisplay.E_DELAY)

    def clear(self):
        with self._lock:
            self.__lcd_byte(LCDisplay.LCD_LINE_1, LCDisplay.LCD_CMD)
            for i in range(16):
                self.__lcd_byte(ord(" "), LCDisplay.LCD_CHR)
            self.__lcd_byte(LCDisplay.LCD_LINE_2, LCDisplay.LCD_CMD)
            for i in range(16):
                self.__lcd_byte(ord(" "), LCDisplay.LCD_CHR)
            self.__lcd_byte(LCDisplay.LCD_LINE_1, LCDisplay.LCD_CMD)

    def write(self, message):
        with self._lock:
            # print("Message : " + message + " naar LCD")
            for i in range(len(message)):
                self.__lcd_byte(ord(message[i]), LCDisplay.LCD_CHR)
                if i == 15:
                    self.__lcd_byte(LCDisplay.LCD_LINE_2, LCDisplay.LCD_CMD)
                if i == 31:
                    self.__lcd_byte(LCDisplay.LCD_SCROLL, LCDisplay.LCD_CMD)

    def write_line(self, message, line):
        with self._lock:
            self.__lcd_byte(0x80 | line - 1 << 6, LCDisplay.LCD_CMD)
            for c in message:
                self.__lcd_byte(ord(c), LCDisplay.LCD_CHR)


if __name__ == "__main__":
    lcd = LCDisplay(26, 13)
    lcd.write("NMCT Box")
    time.sleep(1)
    for i in range(3):
        lcd.write_line("Line {}".format(i), i)
    time.sleep(1)
