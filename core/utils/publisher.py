
class Publisher:

    def __init__(self):
        self._listeners = []

    def register_listener(self, listener):
        self._listeners.append(listener)

    def publish(self, value):
        for handler in self._listeners:
            handler(value)
