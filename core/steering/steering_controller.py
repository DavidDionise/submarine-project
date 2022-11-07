import logging
from gpiozero import Servo


class SteeringController:
    def __init__(self, compass_publisher, set_head, gpio_pin):
        """

        Args:
            compass_publisher (CompassPublisher): used to listen for direction changes
            set_head (int): Desired direction of travel
            gpio_pin (int): Pin on Raspberry PI that servo is getting input from
        """
        self._servo = Servo(gpio_pin)
        self._compass_publisher = compass_publisher
        self._set_head = set_head
        self._gpio_pin = gpio_pin
        self._angle_to_servo_duration_map = _generate_angle_to_servo_duration_map()

        compass_publisher.register_listener(self.angle_change_handler)

    def angle_change_handler(self, angle):
        angle_of_deviation = _calculate_angle_of_deviation(
            angle, self._set_head)

        # Center for the servo motor is 90°, with a range of 0° to 180°. Need
        # to modify the value we get back from the angle of deviation to fit
        # the servo

        servo_angle_of_deviation = angle_of_deviation + 90

        if servo_angle_of_deviation < 0:
            servo_angle_of_deviation = 0
        elif servo_angle_of_deviation > 180:
            servo_angle_of_deviation = 180

        servo_value = self._angle_to_servo_duration_map[servo_angle_of_deviation]

        logging.debug(f"Value sent to servo: {servo_value}")

        self._servo.value = servo_value


def _calculate_angle_of_deviation(current_read, set_head):
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


def _generate_angle_to_servo_duration_map(min=0, max=180):
    return {k: _angle_to_servo_duration(k) for k in range(min, max + 1)}


def _angle_to_servo_duration(angle):
    """Maps compass angle to servo value. Servo values are -1 >= n <= 1
    eg. 0° -> -1, 90° -> 0, 180° -> 1

    Args:
        angle (int): Angle in degrees between 0 and 180

    Returns:
        dictionary: Degree values as key, and servo duration as value
    """

    if angle == 0:  # Avoid div by 0 error
        return -1
    else:
        return float(f'{-1.0 + 2.0 / (180.0 / angle):.2f}')
