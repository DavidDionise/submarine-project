
from ws_client.init_config import config
import websocket
import rel
import logging
from core.compass.compass_publisher import CompassPublisher
from core.steering.steering_controller import SteeringController
from core.hardware_coordinator.hardware_coordinator import HardwareController


class WebSocketController:

    def __init__(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(config["local"]["server_host"],
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)

        # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
        ws.run_forever(dispatcher=rel, reconnect=5)
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()

        self._compass_publisher = CompassPublisher()

    def on_message(self, ws, message):
        if message["status"] == "STOP" and self._hardware_controller != None:
            self._hardware_controller.stop_hardware()

        else:
            set_head = int(message["data"]["setHead"])
            steering_controller = SteeringController(
                compass_publisher=self._compass_publisher,
                set_head=set_head,
                servo_min_angle=113,
                servo_max_angle=211,
                gpio_pin=18
            )
            self._hardware_controller = HardwareController(
                compass_publisher=self._compass_publisher,
                steering_controller=steering_controller
            )

            self._hardware_controller.start_hardware()

    def on_error(self, ws, error):
        logging.error(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.warn(
            f"Connection closed. Status code: {close_status_code} -- Message: {close_msg}")

    def on_open(self, ws):
        logging.info("Opened connection")


if __name__ == "__main__":
    WebSocketController()
