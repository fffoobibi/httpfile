# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 11:15
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : dialogs.py
# @Software: PyCharm
import types
from typing import Callable, Optional

from typing_extensions import Literal

from PyQt5.QtCore import Qt, QEvent, QPoint, QSize
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QGraphicsDropShadowEffect, QApplication, QFrame, QHBoxLayout, \
    QLabel, QSpacerItem, QSizePolicy, QPushButton

# from log_utils import debug_print
from pyqt5utils.components.mixin import KeepAliveAndCloseMixIn, KeepMoveTogetherMixIn

__all__ = ('ShadowDialog',)

from pyqt5utils.components.styles import StylesHelper


class ShadowDialog(QDialog, KeepAliveAndCloseMixIn, KeepMoveTogetherMixIn):

    def set_keep(self, val: bool):
        self._keep = val

    @property
    def when_close(self):
        return self._when_close

    @when_close.setter
    def when_close(self, func: Optional[Callable]):
        if func is not None:
            if isinstance(func, types.MethodType):
                self._when_close = func
            else:
                self._when_close = func

    def __init__(self, title='弹窗', show_title=False, title_style: str = None, frame_less_style: str = None,
                 shadow_color='gray', *a, **kw):
        super(ShadowDialog, self).__init__(*a, **kw)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._keep = False
        self._move_flag = False
        self._when_close = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(5, 5, 5, 5)

        self.frame_less = QWidget()
        self.frame_less.setObjectName('FrameLess')
        self.frame_less.setStyleSheet(
            frame_less_style or '#FrameLess{background:white;color:black;font-family:微软雅黑;border-radius:5px;border:none}')
        lay.addWidget(self.frame_less)

        self._lay = QVBoxLayout(self.frame_less)
        self._lay.setContentsMargins(5, 5, 5, 5)
        if show_title:
            fr = QFrame()
            fr.setStyleSheet('QLabel{font-family:微软雅黑; font-size:11pt; font-weight:bold}')
            fr.setFrameShape(QFrame.NoFrame)
            fr_lay = QHBoxLayout(fr)
            fr_lay.setContentsMargins(9, 9, 9, 9)
            label = QLabel(title)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            StylesHelper.add_menu_style(label)
            if title_style:
                label.setStyleSheet(title_style)
            fr_lay.addWidget(label)
            fr_lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
            close_btn = QPushButton()
            close_btn.setStyleSheet('QPushButton{border:none;background: transparent;font-family:微软雅黑}')
            close_btn.clicked[bool].connect(lambda e: self.close())
            close_btn.setIcon(QIcon(':/new/日历-删除.svg'))
            close_btn.setIconSize(QSize(20, 20))
            fr_lay.addWidget(close_btn)
            self._lay.addWidget(fr)

        # shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(shadow_color))
        shadow.setBlurRadius(10)
        self.frame_less.setGraphicsEffect(shadow)
        self.installEventFilter(self)

    def add_content(self, widget: QWidget):
        self._lay.addWidget(widget)

    def replace_content(self, widget: QWidget, index: int):
        children = self._lay.children()
        self._lay.replaceWidget(children[index], widget)
        self.update()

    def eventFilter(self, a0, a1: QEvent) -> bool:
        if a1.type() == QEvent.WindowDeactivate:
            if not self._keep:
                self.close()
        return QDialog.eventFilter(self, a0, a1)

    def close(self) -> bool:
        super().close()
        if self._when_close:
            try:
                self._when_close()
            except Exception as e:
                pass

    def pop_with_position(self, target: QWidget, position: Literal['l', 't', 'r', 'b'] = 'l', dx: int = 0, dy: int = 0):
        w, h = target.width(), target.height()
        left_point = target.mapToGlobal(QPoint(0, 0))
        delta = QPoint(dx, dy)
        self.raise_()
        self.show()
        if position == 'l':
            self.move(left_point + delta)
        elif position == 'r':
            x = left_point.x() + w - self.width()
            y = left_point.y()
            self.move(QPoint(x, y) + delta)
        elif position == 't':
            x = left_point.x()
            y = left_point.y() - self.height()
            self.move(QPoint(x, y) + delta)
        else:  # b
            x = left_point.x()
            y = left_point.y() + h
            self.move(QPoint(x, y) + delta)

    def pop(self, target: QWidget):
        w, h = target.width(), target.height()
        point = target.mapToGlobal(QPoint(0, h))
        self.move(point + QPoint(-5, 2))
        self.raise_()
        self.show()

    def center(self, target: QWidget = None):
        self.raise_()
        self.show()
        if target is None:
            desk = QApplication.desktop()
            size = desk.screenGeometry()
            w, h = size.width(), size.height()
            w_, h_ = (w - self.width()) / 2, (h - self.height()) / 2
            self.move(w_, h_)
        else:
            left_point = target.mapToGlobal(QPoint(0, 0))
            size = target.size()
            p = self.size() - size
            self.move(QPoint(abs(p.width()), abs(p.height())) / 2 + left_point)
