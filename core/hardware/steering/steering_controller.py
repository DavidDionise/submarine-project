import logging
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from core.sync.event_bus import eventbus


class SteeringController:
    def __init__(self, gpio_pin: int):

        self._servo = Servo(gpio_pin, pin_factory=PiGPIOFactory())
        self._set_head = None
        self._angle_to_servo_duration_map = _generate_angle_to_servo_duration_map()

        eventbus.subscribe("compass-change", self.angle_change_handler)
        eventbus.subscribe("run", self.update_set_head)
        eventbus.subscribe("update", self.update_set_head)
        eventbus.subscribe("stop", self.stop)

    async def angle_change_handler(self, angle: int):
        if self._set_head == None:
            logging.error("\"set_head\" set to None")
            return

        angle_of_deviation = _calculate_angle_of_deviation(
            angle, self._set_head)

        if angle_of_deviation < -90:
            servo_angle_of_deviation = -90
        elif angle_of_deviation > 90:
            servo_angle_of_deviation = 90
        else:
            servo_angle_of_deviation = angle_of_deviation

        servo_value = self._angle_to_servo_duration_map[servo_angle_of_deviation]

        logging.debug(f"Value sent to servo: {servo_value}")

        self._servo.value = servo_value

    async def update_set_head(self, data: dict):
        self._set_head = data["set_head"]

    async def stop(self):
        self._servo.value = 0


def _calculate_angle_of_deviation(current_read: int, set_head: int) -> int:
    """Calculates angle of deviation (ie, smallest angle) between current_read and set_head

    Args:
        current_read (int): _description_
        set_head (int): _description_

    Returns:
        int:
    """

    angle = current_read - set_head

    if angle < -180:
        return angle + 360
    elif angle > 180:
        return angle - 360
    else:
        return angle


def _generate_angle_to_servo_duration_map(min: int = -90, max: int = 90) -> dict:
    return {k: _angle_to_servo_duration(k) for k in range(min, max + 1)}


def _angle_to_servo_duration(angle):
    """Maps compass angle to servo value. Servo values are -1 >= n <= 1. Possible angles are 0 >= n <= 180
    eg. 0° -> -1, 90° -> 0, 180° -> 1

    Args:
        angle (int): Angle in degrees between 0 and 180

    Returns:
        dictionary: Degree values as key, and servo duration as value
    """

    if angle == 0:  # Avoid div by 0 error
        return 0
    else:
        return float(f'{2.0 / (180.0 / angle):.2f}')
