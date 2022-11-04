
from core.compass.compass_publisher import CompassPublisher


class SteeringController:
    def __init__(self, compass_publisher, set_head):
        """

        Args:
            compass_publisher (CompassPublisher): used to listen for direction changes
            set_head (int): Desired direction of travel
        """
        self._compass_publisher = compass_publisher

        compass_publisher.register_listener(self.angle_change_handler)

    def angle_change_handler(angle):
        pass
