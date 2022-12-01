import asyncio
import threading

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from .decorators import singleton

__all__ = ('BackgroundWorker', 'WorkerManager')


class BackgroundWorker(QObject):
    done_sig = pyqtSignal(dict)

    class _AsyncThread(QThread):
        def __init__(self, loop) -> None:
            super().__init__()
            self.async_loop = loop

        def run(self):
            asyncio.set_event_loop(self.async_loop)
            self.async_loop.run_forever()

    def __init__(self, keep_error=False):
        super().__init__()
        self.keep_error = keep_error
        self.async_loop = asyncio.new_event_loop()
        self._thread = self._AsyncThread(self.async_loop)
        self.moveToThread(self._thread)
        self._thread.start()
        self.done_sig.connect(self._back_ground_call)

    @classmethod
    def _back_ground_call(cls, res: dict):
        state = res.get('state')
        call_back = res.get('call_back')
        err_back = res.get('err_back')
        error = res.get('error')
        keep_error = res.get('keep_error')
        try:
            if state:
                if call_back:
                    call_back()
            else:
                if err_back:
                    err_back(error)
        except:
            if not keep_error:
                raise

    def add_task(self, func, args=(), kwargs={}, call_back=None, err_back=None):
        handler = self.async_loop.call_soon_threadsafe(
            self._sync_wrapper(
                func, *args, **kwargs, call_back=call_back, err_back=err_back
            )
        )
        return handler

    def _sync_wrapper(self, func, *args, call_back=None, err_back=None):

        def inner():
            try:
                res = func(*args)

                def call():
                    return call_back(res) if call_back else None

                self.done_sig.emit(
                    {
                        "state": True,
                        "ret": res,
                        "func": func.__name__,
                        "call_back": call,
                        "err_back": err_back,
                        "error": None,
                        "keep_error": self.keep_error
                    }
                )

            except Exception as e:
                self.done_sig.emit(
                    {
                        "state": False,
                        "ret": None,
                        "func": func.__name__,
                        "call_back": call_back,
                        "err_back": err_back,
                        "error": e,
                        "keep_error": self.keep_error
                    }
                )

        return inner

    def add_coro(self, coro, call_back=None, err_back=None):
        handler = asyncio.run_coroutine_threadsafe(
            self._async_wrapper(
                coro, call_back, err_back=err_back), self.async_loop
        )
        return handler

    async def _async_wrapper(self, coro, call_back=None, err_back=None):
        try:
            res = await coro

            def call():
                return call_back(res) if call_back else None

            self.done_sig.emit(
                {
                    "state": True,
                    "ret": res,
                    "func": coro.__name__,
                    "call_back": call,
                    "err_back": err_back,
                    "error": None,
                    "keep_error": self.keep_error

                }
            )
        except Exception as e:
            self.done_sig.emit(
                {
                    "state": False,
                    "ret": None,
                    "func": coro.__name__,
                    "call_back": call_back,
                    "err_back": err_back,
                    "error": e,
                    "keep_error": self.keep_error

                }
            )


@singleton
class WorkerManager(object):
    _lock = threading.Lock()
    _values = {}

    def get(self, name: str) -> BackgroundWorker:
        with self._lock:
            ret = self._values.get(name, None)
            if ret is None:
                self._values[name] = BackgroundWorker()
                return self._values[name]
            return ret
