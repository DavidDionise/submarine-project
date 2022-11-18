

import time
import smbus2 as smbus
import logging
from core.sync.event_bus import eventbus
import asyncio
import statistics
import math


class CompassPublisher:

    def __init__(self, i2c_bus: int = 1, i2c_address: hex = 0x70, rate: float = 0.2, lock: asyncio.Lock = asyncio.Lock(), error_threshold: int = 30):

        self._i2c_bus = i2c_bus
        self._i2c_address = i2c_address
        self._rate = rate
        self._status = 'STOPPED'
        self._lock = lock
        self._error_threshold = error_threshold
        self._prev_angles = []

        self._smbus = smbus.SMBus(i2c_bus)

        eventbus.subscribe("run", self.run)
        eventbus.subscribe("stop", self.stop)

    async def run(self, _):
        async with self._lock:
            self._status = 'ACTIVE'

        while True:
            async with self._lock:
                if self._status == 'STOPPED':
                    break

            write = smbus.i2c_msg.write(self._i2c_address, [0x00, 0x31])
            read = smbus.i2c_msg.read(self._i2c_address, 8)

            self._smbus.i2c_rdwr(write, read)

            high_bits, low_bits = read.buf[1:3]
            degrees = _bytes_to_degrees(high_bits, low_bits)

            if self.is_valid_degrees_value(degrees):
                eventbus.publish("compass-change", degrees)
            else:
                logging.warn(f"Angle beyond threshold: {degrees}")

            await asyncio.sleep(self._rate)

    async def stop(self):
        logging.info("Stopping compass")
        async with self._lock:
            self._status = 'STOPPED'

    def is_valid_degrees_value(self, degrees: int) -> bool:
        if len(self._prev_angles) >= 100:
            del self._prev_angles[0]

        self._prev_angles.append(degrees)

        avg = statistics.mean(self._prev_angles)
        if math.fabs(avg - degrees) > self._error_threshold:
            return False
        else:
            return True


def _bytes_to_degrees(b1: bytes, b2: bytes):
    return int(((b1 << 8) + b2) / 10)
