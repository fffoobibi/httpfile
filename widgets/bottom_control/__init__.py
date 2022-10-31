from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QPushButton

tab_bottom_controls = {}


def register(name: str, index: int = 0, icon: str = None):
    def wrapper(clz):
        tab_bottom_controls[clz] = {'name': name, 'icon': icon, 'index': index}
        return clz

    return wrapper


def load_control_widgets():
    from pathlib import Path
    from importlib import import_module
    dir_path = Path(__file__).parent
    for path_ in dir_path.iterdir():
        if path_.name.startswith('control_'):
            file, _ = path_.name.split('.')
            import_module(f'.{file}', 'widgets.bottom_control')
    return tab_bottom_controls


class BottomWidgetMixIn(QObject):
    bottom_btn: QPushButton
    check_state_signal: pyqtSignal

    def bottom_clicked_slot(self):
        pass

    def check_state_signal_slot(self, checked: bool):
        pass
