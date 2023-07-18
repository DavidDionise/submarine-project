import asyncio
import os
import logging
from gotify import AsyncGotify
import core.utils.cli_logger_init
from gotify_client.init_config import config
from core.hardware.compass.compass_publisher import CompassPublisher
from core.hardware.esc_motor.esc_motor_controller import EscMotorController
from core.hardware.steering.steering_controller import SteeringController

env = os.environ["ENV"]
client_token = os.environ["CLIENT_TOKEN"]


class GotifyClient:
    def __init__(self):
        self._esc_motor_controller = EscMotorController(gpio_pin=12)
        self._compass_publisher = CompassPublisher()
        self._steering_controller = SteeringController(gpio_pin=18)

    async def run(self):
        try:
            logging.info("Starting Gotify WS Client")

            ws_client = AsyncGotify(
                base_url=config[env]["server_host"],
                client_token=client_token,
            )

            async for msg in ws_client.stream():
                logging.info(f"message: {msg}")

        except BaseException as e:
            logging.error(f"{e}")


if __name__ == "__main__":
    asyncio.run(GotifyClient().run())
