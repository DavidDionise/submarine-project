from core.hardware.compass.compass_publisher import CompassPublisher
from core.hardware.esc_motor.esc_motor_controller import EscMotorController
from core.hardware.steering.steering_controller import SteeringController
from sse_client.init_config import config
from sseclient import SSEClient
import logging
import os
import json
import time
import core.utils.cli_logger_init
import asyncio
from gpiozero import LED

env = os.environ["ENV"]


class SseClient:
    def __init__(self):
        self._esc_motor_controller = EscMotorController(gpio_pin=12)
        self._compass_publisher = CompassPublisher()
        self._steering_controller = SteeringController(gpio_pin=18)

    async def run(self):
        while True:
            try:
                logging.info(
                    f'Connecting to SSE Server at {config[env]["server_host"]}'
                )
                self.read_messages()
            except BaseException as e:
                logging.error(f"{e}\n\nRetrying in 3 seconds")
                time.sleep(3)

    def read_messages(self):
        url = f'{config[env]["server_host"]}/events/device'
        messages = SSEClient(url)

        for message in messages:
            logging.debug(f"Message: {message.data}")
            command = json.loads(message.data)
            self.process_command(command)

    def process_command(self, command: dict):
        pass


if __name__ == "__main__":
    asyncio.run(SseClient().run())
