

import time
from core.publisher import Publisher
import smbus2 as smbus
import logging


class CompassPublisher(Publisher):

    def __init__(self, i2c_bus=1, i2c_address=0x70, rate=0.2):
        """Initializes the CompassController with i2c bus properties
        and fetch rate of the compass

        Args:
            i2c_bus (int, optional):  Defaults to 1.
            i2c_address (hexadecimal, optional):  Defaults to 0x70.
            rate (float, optional): Duration in seconds between direction publishes Defaults to 0.2.
        """

        super().__init__()

        self._i2c_bus = i2c_bus
        self._i2c_address = i2c_address
        self._rate = rate
        self._status = 'STOPPED'

        self._smbus = smbus.SMBus(i2c_bus)

    def run(self):
        while True:
            self._status = 'ACTIVE'

            if self._status == 'STOPPED':
                break

            write = smbus.i2c_msg.write(self._i2c_address, [0x00, 0x31])
            read = smbus.i2c_msg.read(self._i2c_address, 8)

            self._smbus.i2c_rdwr(write, read)

            high_bits, low_bits = read.buf[1:3]
            degress = _bytes_to_degrees(high_bits, low_bits)

            logging.debug(f"Compass Degrees: {degress}")
            self.publish(degress)

            time.sleep(self._rate)

    def stop(self):
        self._status = 'STOPPED'


def _bytes_to_degrees(b1, b2):
    return int(((b1 << 8) + b2) / 10)
