

import time
from core.publisher import Publisher
import smbus2 as smbus
import logging


class CompassPublisher(Publisher):

    def __init__(self, i2c_bus=1, i2c_address=0x70, rate=0.2):
        """
        Initializes the CompassController with i2c bus properties
        and fetch rate of the compass
        :param bus: The bus number of the i2c device (default 1)
        :type bus: int
        :param i2c_address: Address of the compass (defaults to 0x70 for use with G7 26 compass)
        :type i2c_address: 
        :param rate: Rate in seconds of new compass readings (default 0.2)
        """

        super().__init__()

        self._i2c_bus = i2c_bus
        self._i2c_address = i2c_address
        self._rate = rate

        self._smbus = smbus.SMBus(i2c_bus)

    def run(self):
        while True:
            write = smbus.i2c_msg.write(self._i2c_address, [0x00, 0x31])
            read = smbus.i2c_msg.read(self._i2c_address, 8)

            self._smbus.i2c_rdwr(write, read)

            high_bits, low_bits = read.buf[1:3]
            degress = _bytes_to_degrees(high_bits, low_bits)

            logging.debug("Compass Degrees: ", degress)
            self.publish(degress)

            time.Sleep(self._rate)


def _bytes_to_degrees(b1, b2):
    return ((b1 << 8) + b2) / 10