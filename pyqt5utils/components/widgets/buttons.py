# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 11:17
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : buttons.py
# @Software: PyCharm
from PyQt5.QtCore import QRect, Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QFont, QPen, QPainterPath, QColor, QMouseEvent, QPixmap, QPaintEvent
from PyQt5.QtWidgets import QPushButton, QWidget


class CorNerButton(QPushButton):

    def __init__(self, *a, **kw):
        self._cornet_bk = kw.pop('color', QColor('#3592C4'))
        self._corner_text = ''
        super(CorNerButton, self).__init__(*a, **kw)

    def set_cornet_text(self, st):
        if st == '0':
            self.clear()
            return
        self._corner_text = st
        self.update()

    def clear(self):
        self._corner_text = ''
        self.update()

    def paintEvent(self, a0) -> None:
        super(CorNerButton, self).paintEvent(a0)

        if self._corner_text:
            if len(self._corner_text) == 1:
                w = '99'
            else:
                w = self._corner_text
            painter = QPainter()
            painter.begin(self)
            painter.setFont(QFont('微软雅黑', 8))
            painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing, True)
            fm = painter.fontMetrics()
            if len(w) <= 2:
                size = fm.width(w) + 4
                path = QPainterPath()
                rect = QRect(self.width() - size, 0, size, size)
                path.addEllipse(QRectF(rect))
            else:
                size = fm.width(w) + 4
                path = QPainterPath()
                rect = QRect(self.width() - size, 0, size, fm.height())
                path.addRoundedRect(QRectF(rect), 5, 5)
            painter.fillPath(path, Qt.red)
            painter.setPen(Qt.white)
            painter.drawText(rect, Qt.AlignCenter, self._corner_text)
            painter.end()

        if self.isChecked():
            painter = QPainter(self)
            painter.setFont(QFont('微软雅黑', 8))
            painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing, True)
            fm = painter.fontMetrics()
            size = fm.width(self.text())
            w, h = self.width(), self.height()
            painter.setPen(QPen(self._cornet_bk, 2))
            under_line_size = min(size, 40)
            painter.drawLine((w - under_line_size) / 2, h - 2, w - (w - under_line_size) / 2, h - 2)


class RotateIconButton(QWidget):
    clicked = pyqtSignal(bool)

    def __init__(self, padding=2, icon_size=18):
        super(RotateIconButton, self).__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.__time_id = None
        self.__rotate = 0
        self.__icon = None
        self.__padding = padding
        self.__icon_size = icon_size

        self.setFixedWidth(padding * 2 + icon_size)
        self.setFixedHeight(padding * 2 + icon_size)

    @property
    def loading(self):
        return bool(self.__time_id)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if self.__time_id:
            self.__rotate += 10
            self.__rotate %= 360
            self.update()

    def stop(self):
        if self.__time_id is not None:
            self.killTimer(self.__time_id)
        self.__time_id = None
        self.__rotate = 0
        self.update()

    def setIcon(self, pixmap: str):
        self.__icon: QPixmap = QPixmap(pixmap).scaled(self.__icon_size, self.__icon_size, transformMode=Qt.SmoothTransformation)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        super(RotateIconButton, self).mousePressEvent(a0)
        if self.__time_id is None:
            self.__time_id = self.startTimer(35)
            self.clicked.emit(True)
        self.clicked.emit(False)

    def paintEvent(self, a0: QPaintEvent) -> None:
        if self.__icon:
            size = self.size()
            w, h = size.width(), size.height()
            painter = QPainter(self)
            painter.setRenderHints(QPainter.SmoothPixmapTransform)
            painter.translate(w / 2, h / 2)
            painter.rotate(self.__rotate)
            painter.drawPixmap(-self.__icon_size / 2, -self.__icon_size / 2, self.__icon)
