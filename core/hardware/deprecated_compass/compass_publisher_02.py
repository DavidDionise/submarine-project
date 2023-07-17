import asyncio
from core.sync.event_bus import eventbus
import smbus2 as smbus
import logging
import math
import ctypes


class CompassPublisher:
    # Correction to be set after calibration
    # Callibration instructions can be found at https://peppe8o.com/magnetometer-with-raspberry-pi-computers-gy-271-hmc5883l-wiring-and-code/
    xs = 1
    ys = 1.2242424242424244
    xb = 426.88
    yb = 214.36

    # Define registers values from datasheet
    ConfigurationRegisterA = 0x00
    ConfigurationRegisterB = 0x01
    ModeRegister = 0x02

    AxisXDataRegisterMSB = 0x03
    AxisXDataRegisterLSB = 0x04
    AxisZDataRegisterMSB = 0x05
    AxisZDataRegisterLSB = 0x06
    AxisYDataRegisterMSB = 0x07
    AxisYDataRegisterLSB = 0x08

    StatusRegister = 0x09
    IdentificationRegisterA = 0x10
    IdentificationRegisterB = 0x11
    IdentificationRegisterC = 0x12

    MeasurementContinuous = 0x00
    MeasurementSingleShot = 0x01
    MeasurementIdle = 0x03

    def __init__(
        self,
        i2c_bus: int = 1,
        i2c_address=0x1E,
        rate: float = 0.2,
        lock: asyncio.Lock = asyncio.Lock(),
    ):
        self._i2c_bus = i2c_bus
        self._i2c_address = i2c_address
        self._rate = rate
        self._status = "STOPPED"
        self._lock = lock

        self._smbus = smbus.SMBus(i2c_bus)

        # Values obtained from https://www.magnetic-declination.com/#
        self.set_declination(-7, 68)

        # Set continuous mode
        self._smbus.write_byte_data(
            self._i2c_address, self.ModeRegister, self.MeasurementContinuous
        )

        eventbus.subscribe("run", self.run)
        eventbus.subscribe("stop", self.stop)

    def _get_x_y(self):
        x_msb = self._smbus.read_byte_data(self._i2c_address, self.AxisXDataRegisterMSB)
        x_lsb = self._smbus.read_byte_data(self._i2c_address, self.AxisXDataRegisterLSB)
        y_msb = self._smbus.read_byte_data(self._i2c_address, self.AxisYDataRegisterMSB)
        y_lsb = self._smbus.read_byte_data(self._i2c_address, self.AxisYDataRegisterLSB)

        # Z must be read to read subsequent values from magnometer
        self._smbus.read_byte_data(self._i2c_address, self.AxisZDataRegisterMSB)
        self._smbus.read_byte_data(self._i2c_address, self.AxisZDataRegisterLSB)

        x = ctypes.c_int16((x_msb << 8) | x_lsb).value
        y = ctypes.c_int16((y_msb << 8) | y_lsb).value

        if x == -4096 or y == -4096:
            logging.warn(f"Bad reading -- x: {x} y: {y}")
            return None, None

        # Apply callibration corrections
        x = x * self.xs + self.xb
        y = y * self.ys + self.yb

        return x, y

    def get_heading_rad(self):
        x, y = self._get_x_y()
        if x == None or y == None:
            return None

        heading_rad = math.atan2(y, x) + self._declination

        # Correct for reversed heading
        if heading_rad < 0:
            heading_rad += 2 * math.pi

        # Check for wrap and compensate
        if heading_rad > 2 * math.pi:
            heading_rad -= 2 * math.pi

        return heading_rad

    def get_heading_degrees(self):
        rad = self.get_heading_rad()
        if rad != None:
            return rad * 180 / math.pi
        else:
            return None

    def set_declination(self, degree, min=0):
        self._declination = (degree + min / 60) * (math.pi / 180)

    async def run(self, _):
        async with self._lock:
            self._status = "ACTIVE"

        while True:
            async with self._lock:
                if self._status == "STOPPED":
                    break

            degrees = self.get_heading_degrees()
            if degrees != None:
                eventbus.publish("compass-change", round(degrees))

            await asyncio.sleep(self._rate)

    async def stop(self):
        logging.info("Stopping compass")
        async with self._lock:
            self._status = "STOPPED"
