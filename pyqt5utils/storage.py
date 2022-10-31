import threading
from werkzeug.local import LocalProxy, LocalStack

from functools import partial

_app_ctx_err_msg = 'use prepare_storage init'
_app_ctx_stack = LocalStack()


def _find_data(name: str):
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(_app_ctx_err_msg)
    return top.get(name)


class Storage(object):
    lock = threading.Lock()
    lock2 = threading.Lock()

    def __init__(self):
        self.queue = []
        self.data = {}

    def push(self, value):
        with self.lock:
            self.queue.append(value)

    def get(self):
        with self.lock:
            return self.queue.pop()

    def set_data(self, key: str, data):
        with self.lock2:
            self.data[key] = data

    def get_data(self, key: str, dft=None):
        with self.lock2:
            return self.data.get(key, dft)

    def clear_all(self):
        with self.lock, self.lock2:
            self.queue.clear()
            self.data.clear()

    def clear_stack(self):
        with self.lock:
            self.queue.clear()


def prepare_storage():
    if _app_ctx_stack.top is None:
        _app_ctx_stack.push(Storage())
    else:
        if not isinstance(_app_ctx_stack.top, Storage):
            _app_ctx_stack.push(Storage())


current_storage: Storage = LocalProxy(partial(_find_data, 'storage'))
