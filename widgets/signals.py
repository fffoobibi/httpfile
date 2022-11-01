import typing
from threading import Thread, Event

from blinker import signal
from pyqt5utils.decorators import singleton
from multiprocessing import Queue, Process

from PyQt5.QtCore import QThread

from cached_property import threaded_cached_property, cached_property


class ProcessSignalMixIn(object):

    def fork(self, event: str, *a) -> tuple:
        queue = Queue()
        process = Process(target=self._process_task, args=(event, queue, *a))
        process.start()
        return process, queue

    def _process_task(self, event, queue, *a):
        self.fork_func(queue, *a)

    def fork_func(self, queue, *a):
        pass

    def push_msg(self, queue, v: typing.Any):
        queue.put(v)


class ProcessSignalMixInHelper(object):
    _process_signal_mixin_current_thread = None
    _process_signal_mixin_current_thread_stop_flag = '_process_signal_mixin_current_thread_stop_flag'
    _process_signal_mixin_current_thread_queue = None
    _wait_flag = None

    class _LoopThread(Thread):
        def __init__(self, func, *args):
            super().__init__()
            self._func = func
            self._args = args

        def run(self) -> None:
            self._func(*self._args)

    def when_accept_process_msg(self, msg: typing.Any):
        """
        run in thread
        """
        pass

    def _msg_loop_task(self, queue, wait_event):
        while True:
            msg = queue.get()
            if msg == self._process_signal_mixin_current_thread_stop_flag:
                break
            else:
                self.when_accept_process_msg(msg)
        wait_event.set()

    @cached_property
    def wait_event(self) -> Event:
        return Event()

    def start_msg_loop(self, queue: Queue) -> Thread:

        self.kill_msg_loop()

        t = self._LoopThread(self._msg_loop_task, queue, self.wait_event)
        t.start()

        self._process_signal_mixin_current_thread_queue = queue
        self._process_signal_mixin_current_thread = t
        return t

    def kill_msg_loop(self):
        if self._process_signal_mixin_current_thread_queue:
            self.wait_event.clear()
            self._process_signal_mixin_current_thread_queue.put(self._process_signal_mixin_current_thread_stop_flag)
            self.wait_event.wait()
            self._process_signal_mixin_current_thread_queue = None
            self._process_signal_mixin_current_thread = None
        else:
            self.wait_event.set()


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
        # print('add event', signal_name, signal, call_back)
        self._signals[signal_name] = [signal, call_back]

    def emit(self, signal_name, *a, **kw):
        ret = self._signals.get(signal_name, None)
        if ret:
            signal, call_back = ret
            if signal:
                signal.emit(*a, **kw)
            if call_back:
                call_back(*a, **kw)


app_exit = signal('app_exit')
app_start_up = signal('app_start_up')
signal_manager = SignalManager()
