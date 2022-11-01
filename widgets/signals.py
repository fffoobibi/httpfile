import typing
from threading import Thread

from blinker import signal
from pyqt5utils.decorators import singleton
from multiprocessing import Queue, Process, freeze_support

freeze_support()

app_exit = signal('app_exit')
app_start_up = signal('app_start_up')


@singleton
class SignalManager(object):
    openUrlFile = 'openUrlFile'
    changeSplitSize = 'changeSplitSize'
    changeVSplitSize = 'changeVSplitSize'
    leftTabClicked = 'leftTabClicked'
    bottomButtonClicked = 'bottomButtonClicked'
    info = 'info'
    warn = 'warn'

    def __init__(self):
        self._signals = {}

    def add_event(self, signal_name: str, signal=None, call_back=None):
        print('add event', signal_name, signal, call_back)
        self._signals[signal_name] = [signal, call_back]

    def emit(self, signal_name, *a, **kw):
        ret = self._signals.get(signal_name, None)
        if ret:
            signal, call_back = ret
            if signal:
                signal.emit(*a, **kw)
            if call_back:
                call_back(*a, **kw)


signal_manager = SignalManager()


class ProcessSignalMixIn(object):
    _queues: typing.Dict[str, Queue] = {}

    def fork(self, event: str, *a):
        if self._queues.get(event, None) is None:
            queue = Queue()
            self._queues[event] = queue

        def _threading_task():
            while True:
                data = self._queues[event].get()
                self.when_accept_msg(data)

        def _process_task():
            self.fork_func(*a)
            t = Thread(target=_threading_task)
            t.start()

        process = Process(target=_process_task, args=())
        process.start()
        return process

    def push_msg(self, event, v: typing.Any):
        self._queues[event].put(v)

    def when_accept_msg(self, v: typing.Any):
        pass

    def fork_func(self, *a):
        pass
