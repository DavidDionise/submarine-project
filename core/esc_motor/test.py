from core.esc_motor.esc_motor_controller import EscMotorController
import time
import logging

logging.basicConfig(level=logging.DEBUG)

e = EscMotorController(16)


motor = e.run(0.2)
next(motor)

time.sleep(3)
next(motor)

time.sleep(4)
