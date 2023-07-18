import logging
from core.sync.event_bus import eventbus
from core.hardware.esc_motor.esc_motor_controller import EscMotorController
from core.hardware.compass.compass_publisher import CompassPublisher
from core.hardware.steering.steering_controller import SteeringController
import asyncio
import sys

logging.basicConfig(level=logging.DEBUG)


async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
        None, lambda s=string: sys.stdout.write(s + " ")
    )
    return await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)


async def get_user_input():
    while True:
        value = await ainput("Enter a number")
        if value == "exit":
            break

        try:
            eventbus.publish("compass-change", int(value))
        except BaseException as e:
            logging.error("Value must be a number")


async def main():
    eventbus.publish("run", {"set_head": 270, "esc_servo_value": 0.2})

    await asyncio.create_task(get_user_input())

    await asyncio.sleep(20)

    eventbus.publish("stop")


asyncio.run(main())
