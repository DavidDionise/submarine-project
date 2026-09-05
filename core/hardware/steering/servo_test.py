from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import time

GPIO_PIN = 18  # steering servo, per the project's client configs

servo = Servo(GPIO_PIN, pin_factory=PiGPIOFactory())

try:
    print("Centering...")
    servo.value = 0
    time.sleep(1)

    print("Sweeping to one extreme...")
    servo.value = -1
    time.sleep(1)

    print("Sweeping to the other extreme...")
    servo.value = 1
    time.sleep(1)

    print("Back to center...")
    servo.value = 0
    time.sleep(1)
finally:
    servo.detach()  # stop holding a signal so the servo goes limp