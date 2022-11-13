

import time
from core.utils.publisher import Publisher
import smbus2 as smbus
import logging


class CompassPublisher(Publisher):

    def __init__(self, i2c_bus=1, i2c_address=0x70, rate=0.2, lock=None):
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
        self._lock = lock

        self._smbus = smbus.SMBus(i2c_bus)

    def run(self):
        self.acquire_lock()
        self._status = 'ACTIVE'
        self.release_lock()

        while True:
            self.acquire_lock()
            if self._status == 'STOPPED':
                self.release_lock()
                break
            self.release_lock()

            write = smbus.i2c_msg.write(self._i2c_address, [0x00, 0x31])
            read = smbus.i2c_msg.read(self._i2c_address, 8)

            self._smbus.i2c_rdwr(write, read)

            high_bits, low_bits = read.buf[1:3]
            degress = _bytes_to_degrees(high_bits, low_bits)

            logging.debug(f"Compass Degrees: {degress}")
            self.publish(degress)

            time.sleep(self._rate)

    def stop(self):
        logging.info("Stopping compass")
        self.acquire_lock()
        self._status = 'STOPPED'
        self.release_lock()

    def set_lock(self, lock):
        self._lock = lock

    def acquire_lock(self):
        if self._lock != None:
            self._lock.acquire()

    def release_lock(self):
        if self._lock != None:
            self._lock.release()


def _bytes_to_degrees(b1, b2):
    return int(((b1 << 8) + b2) / 10)
