import time
from gpiozero import Servo
import logging


class EscMotorController:

    def __init__(self, gpio_pin):
        self._motor_active = False
        self._servo = Servo(gpio_pin)

    def run(self, servo_value):
        if self._motor_active:
            logging.warn("Motor already started")
        else:
            self._motor_generator = self.create_motor_generator(servo_value)
            next(self._motor_generator)
            self._motor_active = True

    def stop(self):
        if not self._motor_active:
            logging.warn("Motor not active")
        else:
            next(self._motor_generator)
            self._motor_active = False

    def create_motor_generator(self, servo_value):
        self._servo.value = 0
        logging.info("Motor starting in...")
        for i in range(0, 5):
            logging.info(5 - i)
            time.sleep(1)

        logging.debug(f"Setting servo value to {servo_value}")
        self._servo.value = servo_value
        yield

        logging.info("Stopping motor")
        self._servo.value = 0
        yield
