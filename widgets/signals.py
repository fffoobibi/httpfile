from blinker import signal
from pyqt5utils.decorators import singleton

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
