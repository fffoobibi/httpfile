from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton

from widgets.base import PluginBaseMixIn
from widgets.signals import signal_manager
from . import register


@register(name='', index=1)
class LockBtn(QPushButton, PluginBaseMixIn):
    def __init__(self):
        super(LockBtn, self).__init__()
        self.setCheckable(True)
        ## padding 5px 5px (top, bottom  left,right)
        self.setStyleSheet('QPushButton{background: transparent; border:none; padding:3px 3px; font-family:微软雅黑}'
                           'QPushButton:hover{background: lightgray}')
        name = self.get_register('name')
        icon = self.get_register('icon')
        self.setText(name)
        if icon:
            self.setIcon(QIcon(icon))
        signal_manager.add_event(signal_manager.statusReadOnly, None, call_back=self.update_state)
        self.clicked.connect(self.click_slot)

    def update_state(self, line, col):
        self.setText(f'{line + 1}:{col + 1}')

    def click_slot(self):
        from widgets.mainwidget import MainWidget
        main_app: MainWidget = self.get_app()
        if main_app.tabWidget.count():
            current = main_app.tabWidget.currentWidget()
