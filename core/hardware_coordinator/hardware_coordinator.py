
class HardwareController:

    def __init__(self, compass_publisher, steering_controller):
        self._compass_publisher = compass_publisher
        self._steering_controller = steering_controller

    def start_hardware(self):
        self._compass_publisher.run()

    def stop_hardware(self):
        self._compass_publisher.stop()
