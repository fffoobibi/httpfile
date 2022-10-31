# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 11:17
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : containers.py
# @Software: PyCharm

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect, \
    QStackedWidget, QButtonGroup

from pyqt5utils.components.widgets.buttons import CorNerButton


class StackWidget(QWidget):
    indexChanged = pyqtSignal(int)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._line_color = Qt.black
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)

        self.top_bar = QWidget()
        self.top_bar.setObjectName('TopBar')
        self.top_lay = QHBoxLayout(self.top_bar)
        self.top_lay.setContentsMargins(0, 0, 0, 0)
        self.top_lay.setSpacing(0)
        self.top_spacer = QSpacerItem(40, 40, hPolicy=QSizePolicy.Expanding)
        self.top_lay.addSpacerItem(self.top_spacer)
        self.top_bar.setStyleSheet('QWidget{background: white}')

        graphics = QGraphicsDropShadowEffect()
        graphics.setOffset(0, 2)
        graphics.setBlurRadius(10)
        graphics.setColor(QColor(Qt.lightGray))
        self.top_bar.setGraphicsEffect(graphics)

        self.center = QStackedWidget()

        self.lay.addWidget(self.top_bar, 0)
        self.lay.addWidget(self.center, 1)

        self.top_group = QButtonGroup()

    def set_checked_line(self, color: QColor):
        self._line_color = color

    def add_left_top(self, widget: QWidget):
        self.top_lay.insertWidget(0, widget)

    def append_top(self, widget: QWidget):
        self.top_lay.addWidget(widget)

    def add_tab(self, tab_name: str, widget: QWidget, icon: str = None, msg=''):
        btn = CorNerButton(color=self._line_color)
        btn.setCheckable(True)
        if icon:
            btn.setIcon(QIcon(icon))
        btn.setText(tab_name)
        btn.setStyleSheet(
            'QPushButton{border:none; background:transparent ;padding:10px 10px;font-family:微软雅黑;color:gray}'
            'QPushButton:hover{background:#ECEDEE;border-radius:5px}'
            'QPushButton:pressed{background:#EAEBED; border-radius:5px}'
            'QPushButton:checked{color: black;font-weight:bold}')
        index = self.center.count()
        btn.set_cornet_text(f'{msg}')
        btn.clicked.connect(lambda: (self.center.setCurrentIndex(index), self.indexChanged.emit(index)))
        self.top_group.addButton(btn)
        self.top_lay.removeItem(self.top_spacer)
        self.top_lay.addWidget(btn)
        self.top_lay.addSpacerItem(self.top_spacer)

        self.center.addWidget(widget)
