from core.compass.compass_publisher import CompassPublisher
from core.esc_motor.esc_motor_controller import EscMotorController
from core.hardware_coordinator.hardware_coordinator import HardwareController
from core.steering.steering_controller import SteeringController
from sse_client.init_config import config
from sseclient import SSEClient
import logging
import os
import json
import time
import threading
import core.utils.cli_logger_init
from gpiozero import LED

env = os.environ["ENV"]


class SseClient:
    def __init__(self):
        self._esc_motor_controller = EscMotorController(gpio_pin=16)
        self._compass_publisher = CompassPublisher()
        self._steering_controller = SteeringController(
            compass_publisher=self._compass_publisher,
            gpio_pin=18
        )
        self._hardware_controller = HardwareController(
            compass_publisher=self._compass_publisher,
            steering_controller=self._steering_controller,
            esc_motor_controller=self._esc_motor_controller
        )
        self._hardware_started = False

    def run(self):
        threading.Thread(target=self.handle_process_loop).start()

    def handle_process_loop(self):
        while True:
            try:
                logging.info("Connecting to SSE Server")
                self.read_messages()
            except BaseException as e:
                logging.error(
                    f"{e}\n\nRetrying in 3 seconds")
                time.sleep(3)

    def read_messages(self):
        url = f'{config[env]["server_host"]}/events/device'
        messages = SSEClient(url)
        LED(25).on()

        for message in messages:
            logging.debug(f"Message: {message.data}")
            command = json.loads(message.data)
            self.process_command(command)

    def process_command(self, command):
        if command["status"] == "STOP":
            if self._hardware_started == False:
                logging.warn("Hardware already stopped")
            else:
                logging.info("Received STOP status")
                self._hardware_controller.stop_hardware()
                self._hardware_started = False

        else:
            if self._hardware_started == True:
                logging.warn(
                    "Hardware must be stopped before making an update")
            else:
                set_head = int(command["data"]["setHead"])
                logging.info(
                    f"Received ACTIVE status with setHead: {set_head}")

                threading.Thread(
                    target=self._hardware_controller.start_hardware, args=[set_head]).start()
                self._hardware_started = True


if __name__ == "__main__":
    SseClient().run()
