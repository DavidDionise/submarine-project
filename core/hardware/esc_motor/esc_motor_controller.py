import time
from gpiozero import Servo
import logging
from gpiozero.pins.pigpio import PiGPIOFactory
from core.sync.event_bus import eventbus


class EscMotorController:

    def __init__(self, gpio_pin: int):
        self._motor_active = False
        self._servo = Servo(gpio_pin, pin_factory=PiGPIOFactory())

        eventbus.subscribe("run", self.run)
        eventbus.subscribe("stop", self.stop)

    async def run(self, data):
        servo_value = data["esc_servo_value"]
        if self._motor_active:
            logging.warn("Motor already started")
        else:
            self._servo.value = servo_value
            self._motor_active = True

    async def stop(self):
        if not self._motor_active:
            logging.warn("Motor not active")
        else:
            self._servo.value = 0
            self._motor_active = False
