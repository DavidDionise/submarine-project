
from ws_client.init_config import config
import websocket
import rel
import logging
from core.compass.compass_publisher import CompassPublisher
from core.steering.steering_controller import SteeringController
from core.esc_motor.esc_motor_controller import EscMotorController
from core.hardware_coordinator.hardware_coordinator import HardwareController
import json
import os
import threading

logging.basicConfig(level=logging.INFO)
env = os.environ["ENV"]


class WebSocketController:

    def __init__(self):
        self._hardware_controller = None
        self._timer = None
        self._ws = websocket.WebSocketApp(config[env]["server_host"],
                                          on_open=self.on_open,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close,
                                          on_ping=self.heart_beat
                                          )
        self.init_ws()

    def init_ws(self):
        try:
            logging.info("Connecting to WS server")
            websocket.enableTrace(True)

            # Set dispatcher to automatic reconnection, 3 second reconnect delay if connection closed unexpectedly
            self._ws.run_forever(dispatcher=rel, reconnect=3)
            self._timer = threading.Timer(
                float(config[env]["heart_beat_timeout"]), self.handle_heart_beat_timeout)
            rel.signal(2, rel.abort)  # Keyboard Interrupt
            rel.dispatch()
        except websocket.WebSocketTimeoutException:
            logging.error("Websocket disconnected")

    def handle_heart_beat_timeout(self):
        logging.warn("Hearbeat timed out - reconnecting")
        self._ws.close()
        self.init_ws()

    def heart_beat(self, app, message):
        logging.debug("Received ping")
        if self._timer != None:
            logging.debug("Canceling heart beat timer")
            self._timer.cancel()

        logging.debug("Starting new heart beat timer")
        self._timer = threading.Timer(
            float(config[env]["heart_beat_timeout"]), self.handle_heart_beat_timeout)
        self._timer.start()

    def on_message(self, ws, message_json):
        message = json.loads(message_json)

        if message["status"] == "STOP":
            if self._hardware_controller != None:
                logging.info("Received STOP status")
                self._hardware_controller.stop_hardware()

        else:
            set_head = int(message["data"]["setHead"])
            logging.info(f"Received ACTIVE status with setHead: {set_head}")
            esc_motor_controller = EscMotorController(gpio_pin=16)
            compass_publisher = CompassPublisher()
            steering_controller = SteeringController(
                compass_publisher=compass_publisher,
                set_head=set_head,
                gpio_pin=18
            )
            self._hardware_controller = HardwareController(
                compass_publisher=compass_publisher,
                steering_controller=steering_controller,
                esc_motor_controller=esc_motor_controller
            )

            threading.Thread(
                target=self._hardware_controller.start_hardware).start()

    def on_error(self, ws, error):
        logging.error(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.warn(
            f"Connection closed. Status code: {close_status_code} -- Message: {close_msg}")

    def on_open(self, ws):
        logging.info("Opened connection")


if __name__ == "__main__":
    WebSocketController()
