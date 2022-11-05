import wiringpi
import logging


class SteeringController:
    def __init__(self, compass_publisher, set_head, servo_min_angle, servo_max_angle, gpio_pin):
        """

        Args:
            compass_publisher (CompassPublisher): used to listen for direction changes
            set_head (int): Desired direction of travel
            servo_min_angle (int): Min value for servo steering
            servo_max_angle (int): Max value for servo steering
            gpio_pin (int): Pin on Raspberry PI that servo is getting input from
        """
        self._compass_publisher = compass_publisher
        self._set_head = set_head
        self._servo_min_angle = servo_min_angle
        self._servo_max_angle = servo_max_angle
        self._gpio_pin = gpio_pin
        self._angle_to_servo_duration_map = _generate_angle_to_servo_duration_map()

        compass_publisher.register_listener(self.angle_change_handler)

        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(gpio_pin, wiringpi.GPIO.PWM_OUTPUT)

        # set the PWM mode to milliseconds stype
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)

        # divide down clock
        wiringpi.pwmSetClock(192)
        wiringpi.pwmSetRange(2000)

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

        # Servo lib takes duration multiplied by 100
        servo_duration = int(
            self._angle_to_servo_duration_map[servo_angle_of_deviation] * 100)

        if servo_duration > self._servo_max_angle:
            servo_duration = self._servo_max_angle
        elif servo_duration < self._servo_min_angle:
            servo_duration = self._servo_min_angle

        logging.debug(f"Value sent to servo: {servo_duration}")
        wiringpi.pwmWrite(self._gpio_pin, servo_duration)


def _calculate_angle_of_deviation(current_read, set_head):
    """

    :param current_read: (int) The current angle of the compass
    :param set_head: (int) Desired direction of travel
    :return: Angle of deviation between current read and set head
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
    """Input to servo is the duration of the wavelength in milliseconds - this functions maps an angle to the servo wavelenth.
    eg. 0° -> 1.0 ms, 90° -> 1.5 ms and 180° -> 2.0 ms

    Args:
        angle (int): Angle in degrees between 0 and 180

    Returns:
        dictionary: Degree values as key, and servo duration as value
    """
    if angle == 0:
        return 1.0
    else:
        return float(f'{1.0 + 1.0 / (180.0 / angle):.2f}')
