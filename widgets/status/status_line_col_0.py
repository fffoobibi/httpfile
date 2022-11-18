from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel, QLineEdit

from pyqt5utils.components import Confirm
from widgets.signals import signal_manager
from widgets.base import PluginBaseMixIn

from . import register
from ..factorys import styled_factory


@register(name='', index=0)
class LineCol(QPushButton, PluginBaseMixIn, styled_factory('bottom-button')):
    def __init__(self):
        super(LineCol, self).__init__()
        ## padding 5px 5px (top, bottom  left,right)
        self.setStyleSheet('QPushButton{background: transparent; border:none; padding:3px 10px; font-family:微软雅黑}'
                           'QPushButton:hover{background: lightgray}')
        name = self.get_register('name')
        icon = self.get_register('icon')
        self.setText(name)
        if icon:
            self.setIcon(QIcon(icon))
        signal_manager.add_event(signal_manager.statusLineInfo, None, call_back=self.update_line_col)
        self.clicked.connect(self.click_slot)
        self.setToolTip('转到行 Ctrl+G')

    def update_line_col(self, line, col):
        self.setText(f'{line + 1}:{col + 1}')

    def click_slot(self):
        from widgets.mainwidget import MainWidget
        main_app: MainWidget = self.get_app()
        if main_app.tabWidget.count():
            self.show_move_dialog()

    def show_move_dialog(self):
        def ok():
            current = self.get_app().tabWidget.currentWidget()
            if line.text():
                try:
                    line_, col_ = line.text().split(':')
                except:
                    line_, col_ = line.text(), 1
                current.setFocus()
                current.move_to(int(line_) - 1, int(col_) - 1)
                print(current.file_path())

        content = QWidget()
        lay = QHBoxLayout(content)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(QLabel('[行]:[列]'))
        line = QLineEdit()
        line.setText(self.text())
        lay.addWidget(line)
        Confirm.msg('转到行列', target=self.get_app(), content=content, after_close=ok, after_close_duration=100)
