import logging
import threading


class HardwareController:

    def __init__(self, compass_publisher, steering_controller, esc_motor_controller):
        self._compass_publisher = compass_publisher
        self._steering_controller = steering_controller
        self._esc_motor_controller = esc_motor_controller

        self._compass_publisher.set_lock(threading.Lock())

    def start_hardware(self, set_head):
        logging.info("Starting hardware")
        self._steering_controller.update_set_head(set_head)
        threading.Thread(target=self._esc_motor_controller.run,
                         args=[0.2]).start()
        threading.Thread(target=self._compass_publisher.run).start()

    def stop_hardware(self):
        logging.info("Stopping hardware")
        self._compass_publisher.stop()
        self._esc_motor_controller.stop()
