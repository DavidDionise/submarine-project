import smbus2
import time

bus = smbus2.SMBus(1)
ADDRESS = 0x60

while True:
    high = bus.read_byte_data(ADDRESS, 0x02)
    low = bus.read_byte_data(ADDRESS, 0x03)
    bearing = ((high << 8) | low) / 10.0
    print(f"Heading: {bearing}°")
    time.sleep(0.2)