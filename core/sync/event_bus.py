from functools import wraps
import asyncio
import logging


class EventBus:

    def __init__(self):
        self._events = {}

    def subscribe(self, event: str, handler: callable):
        if event in self._events:
            self._events[event].append(handler)
        else:
            self._events[event] = [handler]

    def unsubscribe(self, event: str, handler: callable):
        self._events[event].remove(handler)

    def publish(self, event: str, data: any = None):
        logging.debug(f"event: {event} -- data: {data}")
        tasks = set()
        for handler in self._events.get(event, []):

            task = asyncio.create_task(
                handler(data) if data != None else handler()
            )
            tasks.add(task)

            task.add_done_callback(tasks.discard)


eventbus = EventBus()
