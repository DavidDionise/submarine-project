
from core.steering.steering_controller import SteeringController
from core.compass.compass_publisher import CompassPublisher
import logging

# logging.getLogger().setLevel(logging.DEBUG)

compass_publisher = CompassPublisher(rate=0.1)
steering_controller = SteeringController(
    compass_publisher=compass_publisher,
    set_head=0,
    gpio_pin=18
)

compass_publisher.run()
