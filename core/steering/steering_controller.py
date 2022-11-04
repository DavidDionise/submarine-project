from core.compass.compass_publisher import CompassPublisher


class SteeringController:
    def __init__(self, compass_publisher, set_head, min_value, max_value):
        """

        Args:
            compass_publisher (CompassPublisher): used to listen for direction changes
            set_head (int): Desired direction of travel
            min_value (int): Min value for servo steering
            max_value (int): Max value for servo steering
        """
        self._compass_publisher = compass_publisher
        self._set_head = set_head
        self._min_value = min_value
        self._max_value = max_value

        compass_publisher.register_listener(self.angle_change_handler)

    def angle_change_handler(self, angle):
        pass

    def calculate_next_angle(self, current_read):
        angle_of_deviation = _calculate_angle_of_deviation(current_read, self._set_head)

        if angle_of_deviation < self._min_value:
            return self._min_value
        elif angle_of_deviation > self._max_value:
            return self._max_value
        else:
            return angle_of_deviation


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
