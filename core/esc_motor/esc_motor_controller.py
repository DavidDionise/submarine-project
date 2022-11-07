import time
from gpiozero import Servo


# class EscMotorController(Motor):
class EscMotorController:

    def run(self, servo_duration):
        s = Servo(20)
        s.value = servo_duration
        time.sleep(5)
