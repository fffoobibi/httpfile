from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel

from widgets.bottom_control import register
from . import BottomWidgetMixIn
from widgets.base import PluginBaseMixIn


@register(name='新闻服务', icon='', index=2)
class NewControlWidget(QWidget, BottomWidgetMixIn, PluginBaseMixIn):
    check_state_signal = pyqtSignal(bool)

    def __init__(self):
        super(NewControlWidget, self).__init__()
        self.label = QLabel(self)
        self.label.setText('行文')
