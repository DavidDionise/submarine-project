import board
import adafruit_lis3mdl
import math
import asyncio
from core.sync.event_bus import eventbus
import logging

i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_lis3mdl.LIS3MDL(i2c, 0x1C)


class CompassPublisher:
    def __init__(self, rate: float = 0.2, lock: asyncio.Lock = asyncio.Lock()):
        self._rate = rate
        self._status = "STOPPED"
        self._lock = lock

        eventbus.subscribe("run", self.run)
        eventbus.subscribe("stop", self.stop)

    async def run(self, _):
        async with self._lock:
            self._status = "ACTIVE"

        while True:
            mag_x, mag_y, mag_z = sensor.magnetic

            angle_radians = math.atan2(mag_y, mag_x)
            angle_degrees = angle_radians * 180 / math.pi
            positive_angle_degrees = int(
                angle_degrees if angle_degrees > 0 else angle_degrees + 360
            )

            eventbus.publish("compass-change", positive_angle_degrees)

            await asyncio.sleep(self._rate)

    async def stop(self):
        logging.info("Stopping compass")
        async with self._lock:
            self._status = "STOPPED"
