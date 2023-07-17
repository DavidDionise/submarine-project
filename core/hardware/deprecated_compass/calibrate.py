import smbus2 as smbus
import sys
import logging

logging.basicConfig(level=logging.INFO)

i2c_bus = 1
i2c_address = 0x70

bus = smbus.SMBus(i2c_bus)

if len(sys.argv) == 1:
    raise Exception("Must include either \"start\" or \"end\" argument")

read = smbus.i2c_msg.read(i2c_address, 8)
if sys.argv[1] == "start":
    command = 0xC0
elif sys.argv[1] == "end":
    command = 0xC1
else:
    raise Exception(f"Unknown command: {sys.argv[1]}")

write = smbus.i2c_msg.write(i2c_address, [0x00, command])

bus.i2c_rdwr(write, read)

logging.info(f"Command sent with response {bytes(read)}")
