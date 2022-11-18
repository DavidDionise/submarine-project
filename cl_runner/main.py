
import logging
from core.sync.event_bus import eventbus
from core.hardware.esc_motor.esc_motor_controller import EscMotorController
from core.hardware.compass.compass_publisher import CompassPublisher
from core.hardware.steering.steering_controller import SteeringController
import asyncio

logging.basicConfig(level=logging.DEBUG)


async def main():
    compass_controller = CompassPublisher(error_threshold=60)
    steering_controller = SteeringController(gpio_pin=18)

    eventbus.publish("run", {"set_head": 180})

    await asyncio.sleep(100)

    eventbus.publish("stop")


asyncio.run(main())
