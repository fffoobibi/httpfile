import threading

from pyqt5utils.decorators import singleton
from ._types import ControllerTypes


@singleton
class ControllerManager(object):
    _values = {}
    _lock = threading.Lock()

    def get(self, type: ControllerTypes):
        with self._lock:
            return self._values.get(type)

    def register(self, type: ControllerTypes, controller):
        with self._lock:
            self._values[type] = controller

    def values(self):
        return self._values
