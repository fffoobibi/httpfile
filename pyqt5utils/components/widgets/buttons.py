# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 11:17
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : buttons.py
# @Software: PyCharm
from PyQt5.QtCore import QRect, Qt, QRectF
from PyQt5.QtGui import QPainter, QFont, QPen, QPainterPath, QColor
from PyQt5.QtWidgets import QPushButton


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
