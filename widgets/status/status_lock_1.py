from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QApplication

from widgets.base import PluginBaseMixIn
from widgets.signals import signal_manager
from . import register
from ..factorys import styled_factory


@register(name='', index=1)
class LockBtn(QPushButton, PluginBaseMixIn, styled_factory('bottom-button')):
    def __init__(self):
        super(LockBtn, self).__init__()
        self.setCheckable(True)
        self._un_lock = ':/icon/解锁.svg'
        self._lock = ':/icon/锁定.svg'
        ## padding 5px 5px (top, bottom  left,right)
        self.setStyleSheet('QPushButton{background: transparent; border:none; padding:3px 3px; font-family:微软雅黑}'
                           'QPushButton:hover{background: lightgray}')
        name = self.get_register('name')
        # icon = self.get_register('icon')

        self.setText(name)
        self.setIcon(QIcon(self._un_lock))
        signal_manager.add_event(signal_manager.statusReadOnly, None, call_back=self.update_state)
        self.clicked.connect(self.click_slot)

    def update_state(self, line, col):
        self.setText(f'{line + 1}:{col + 1}')

    def click_slot(self):
        from widgets.mainwidget import MainWidget
        main_app: MainWidget = self.get_app()
        if self.isChecked():
            self.setIcon(QIcon(self._lock))
            lock = True
        else:
            self.setIcon(QIcon(self._un_lock))
            lock = False
        signal_manager.emit(signal_manager.statusReadOnly, lock)
        for index in range(main_app.tabWidget.count()):
            try:
                QApplication.processEvents()
                main_app.tabWidget.widget(index).set_read_only(lock)
            except:
                import traceback
                traceback.print_exc()
