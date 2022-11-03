

from core.publisher import Publisher
import smbus2 as smbus
import logging


class CompassController(Publisher):

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
        self._i2c_bus = i2c_bus
        self._i2c_address = i2c_address
        self._rate = rate

        self._smbus = smbus.SMBus(i2c_address)

    def bytes_to_degrees(b1, b2):
        return ((b1[0] << 8) + b2[0]) / 10

    def run(self):
        while True:
            write = smbus.i2c_msg.write(self._address, [0x00, 0x31])
            read = smbus.i2c_msg.read(self._i2c_address, 8)

            self._smbus.i2c_rdwr(write, read)

            high_bits, low_bits = read[1:3]
            degress = self.bytes_to_degrees(high_bits, low_bits)

            logging.debug("Compass Degrees: ", degress)
            self.publish(degress)
