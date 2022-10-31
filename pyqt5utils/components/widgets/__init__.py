# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 10:40
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : __init__.py.py
# @Software: PyCharm
import time
from datetime import date, datetime
from typing import Tuple, Union, Callable, re

from PyQt5.QtCore import Qt, pyqtSignal, QRect, QDate, QRectF, QEvent, QPoint
from PyQt5.QtGui import QTextCharFormat, QPainter, QColor, QPainterPath, QMovie, QIcon
from PyQt5.QtWidgets import QDialog, QCalendarWidget, QPushButton, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QVBoxLayout, QWidget, QGraphicsDropShadowEffect, QLineEdit, QLabel

from pyqt5utils.components.styles import Sh


class ValidateLine(QLineEdit):
    validate_fail = pyqtSignal()
    validate_success = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_validator = None
        self.required = True
        self.validate_flag = False
        self._validators = []

    def validate_(self) -> Tuple[bool, str]:
        for val, _ in self._validators:
            flag, msg = val(self.text())
            if not flag:
                return False, msg
        return True, '验证通过'

    def validate(self, text: str = None) -> bool:
        self.validate_flag = True
        t = text or self.text().strip()
        if self.required:
            if not t:
                self.validate_fail.emit()
                return False
        if self.custom_validator:
            if self.custom_validator.search(t) is None:
                self.validate_fail.emit()
                return False
            else:
                self.validate_success.emit()
                return True
        self.validate_flag = False
        return True
# clG3rnBp
    def setCustomValidator(self, pattern: Union[str, Callable], msg: str = ''):
        if isinstance(pattern, str):
            self._validators.append([pattern, msg])
            self.custom_validator = lambda v: re.compile(
                pattern, re.IGNORECASE).search(v)
        else:
            self._validators.append([pattern, msg])
            self.custom_validator = pattern


class ValidateLineEx(ValidateLine):
    def __init__(self, *a, **kw):
        super(ValidateLineEx, self).__init__(*a, **kw)

    def set_place_holder(self, text):
        self.setPlaceholderText(text)

    def validate(self, msg: str = None, show=False) -> bool:
        for pattern, msg in self._validators:
            if isinstance(pattern, str):
                pat = re.compile(pattern).search(self.text())
            else:
                pat = pattern(self.text())
            flag, m = pat
            if not flag:
                # if show:
                #     v = Toast.make_text(msg, self, keep=False)
                #     try:
                #         v.setFocusPolicy(Qt.NoFocus)
                #         self.setFocus(Qt.MouseFocusReason)
                #     except:
                #         import traceback
                #         traceback.print_exc()
                return False
        return True

    def validate_(self) -> Tuple[bool, str]:
        for val, _ in self._validators:
            flag, msg = val(self.text())
            if not flag:
                return False, msg
        return True, '验证通过'


class ComboLine(ValidateLine):
    add_sig = pyqtSignal(str)
    pop_sig = pyqtSignal(str)
    search_flag = pyqtSignal()
    click_signal = pyqtSignal()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.textEdited.connect(self.pop_sig)
        self.textEdited.connect(lambda v: self.search_flag.emit())
        self.setClearButtonEnabled(False)

    def focusOutEvent(self, a0) -> None:
        super(ComboLine, self).focusOutEvent(a0)
        if self.text().strip():
            self.add_sig.emit(self.text())

    def mousePressEvent(self, a0) -> None:
        super().mousePressEvent(a0)
        if a0.button() == Qt.LeftButton:
            self.click_signal.emit()


class CalendarDialog(QDialog):
    pre_month_style = '''
        QToolButton#qt_calendar_prevmonth {
        background: transparent;
        border: none;
        width: 40px;
        qproperty-icon: url(:/double/后退面性-正常.svg);
        }
    '''

    next_month_style = '''
        QToolButton#qt_calendar_nextmonth {
        background: transparent;
        border: none;
        width: 40px;
        qproperty-icon: url(:/double/前进面性-正常.svg);
    }'''

    calendar_calendarview_style = '''
        /* #qt_calendar_calendarview */
        QAbstractItemView {
            outline: 0px;/*去掉选中后的虚线框*/
            color: black;
        selection-color: white;
        selection-background-color: rgb(255, 174, 0);
        }
        QAbstractItemView:disabled{
        color:#D3D3D3;
        }
        QAbstractItemView:enabled{
        color:#333333;}
    '''

    ok_signal = pyqtSignal(date)

    class _CalendarWidget(QCalendarWidget):
        _color = (109, 139, 222)

        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self._set_weekday_fmt()

        def _set_weekday_fmt(self):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(*self._color))
            self.setWeekdayTextFormat(Qt.Saturday, fmt)
            self.setWeekdayTextFormat(Qt.Sunday, fmt)

        def paintCell(self, painter: QPainter, rect: QRect, _date: QDate):
            if _date > self.maximumDate() or _date < self.minimumDate():
                painter.save()
                painter.setPen(Qt.lightGray)
                painter.drawText(rect, Qt.TextSingleLine | Qt.AlignCenter, str(_date.day()))
                painter.restore()

            elif _date.dayOfWeek() in [6, 7]:
                painter.save()
                painter.setRenderHints(QPainter.Antialiasing, True)
                if _date == self.selectedDate():
                    path = QPainterPath()
                    path.addRect(QRectF(rect))
                    # path.addEllipse(QRectF(rect))
                    painter.fillPath(path, QColor(*self._color))
                    painter.setPen(Qt.white)

                painter.drawText(rect, Qt.TextSingleLine | Qt.AlignCenter, str(_date.day()))
                painter.restore()
            else:
                QCalendarWidget.paintCell(self, painter, rect, _date)

    def __init__(self):
        super(CalendarDialog, self).__init__()
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        pannel_lay = QVBoxLayout(self)
        pannel_lay.setContentsMargins(5, 5, 5, 5)
        self.frame_less = QWidget()
        self.frame_less.setObjectName('FrameLess')
        self.frame_less.setStyleSheet(
            '#FrameLess{background:white;color:black;font-family:微软雅黑;border-radius:5px;border:none}'
            'QWidget{background:white;color:black;font-family:微软雅黑}' + Sh.menu_style + self.pre_month_style +
            self.next_month_style + self.calendar_calendarview_style)
        pannel_lay.addWidget(self.frame_less)

        lay = QVBoxLayout(self.frame_less)
        lay.setContentsMargins(5, 5, 5, 5)

        self.calendar = self._CalendarWidget()
        self.calendar.setGridVisible(False)

        fr = QFrame()
        self.timer_lay = QHBoxLayout(fr)
        self.timer_lay.setContentsMargins(0, 0, 0, 0)
        fr.setFrameShape(QFrame.NoFrame)
        self.timer_lay.addWidget(self.calendar, stretch=10)

        # list = QListWidget()
        # list.setFixedWidth(50)
        # list.addItems([f'{i}'.zfill(2) for i in range(24)])
        # list.setStyleSheet(Sh.list_page_style)
        # list.verticalScrollBar().setStyleSheet(Sh.history_v_scroll_style)
        # self.timer_lay.addWidget(list)
        #
        # list = QListWidget()
        # list.setFixedWidth(50)
        # list.addItems([f'{i}'.zfill(2) for i in range(60)])
        # list.setStyleSheet(Sh.list_page_style)
        # list.verticalScrollBar().setStyleSheet(Sh.history_v_scroll_style)
        # self.timer_lay.addWidget(list)

        lay.addWidget(fr)

        frame = QFrame()
        f_lay = QHBoxLayout(frame)
        f_lay.setContentsMargins(3, 0, 0, 0)

        self.current_btn = QPushButton('此刻')
        self.current_btn.setStyleSheet('QPushButton{color:  #426BDD;border:none}')
        self.current_btn.clicked.connect(self.select_current)

        self.ok_btn = QPushButton('确认')
        self.ok_btn.setStyleSheet(
            'QPushButton{font-family:微软雅黑;padding:3px; background: #426BDD;color:white;border:1px solid #426BDD;border-radius:3px}'
            'QPushButton:hover{background: rgb(109,139,222);border:1px solid rgb(109,139,222)}')
        self.ok_btn.clicked.connect(self.ok_slot)

        f_lay.addWidget(self.current_btn)
        f_lay.addSpacerItem(QSpacerItem(40, 40, hPolicy=QSizePolicy.Expanding))
        f_lay.addWidget(self.ok_btn)

        lay.addWidget(frame)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.black)
        shadow.setBlurRadius(10)
        self.frame_less.setGraphicsEffect(shadow)
        self.installEventFilter(self)

    def select_current(self):
        self.calendar.setSelectedDate(datetime.now())
        self.calendar.showSelectedDate()

    def ok_slot(self):
        self.ok_signal.emit(self.calendar.selectedDate().toPyDate())
        self.close()

    def eventFilter(self, a0, a1: QEvent) -> bool:
        if a1.type() == QEvent.WindowDeactivate:
            self.close()
        return QDialog.eventFilter(self, a0, a1)

    def pop(self, target: QWidget):
        w, h = target.width(), target.height()
        point = target.mapToGlobal(QPoint(0, h))
        self.move(point + QPoint(-5, 2))
        self.raise_()
        self.show()


class GifLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setGif(self, file_name: str) -> None:
        self._movie = QMovie(file_name)
        self._movie.setSpeed(100)
        self.setMovie(self._movie)
        self.movie().start()

    def removeGif(self, text):
        self.setText(text)

    def mousePressEvent(self, event: 'QMouseEvent') -> None:
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class GifButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movie = None
        self._is_loading = False
        self._text: str = ''
        self._start_time = -1
        self._loading_flag = '.'
        self._dynamic = False

    def removeGif(self, icon: str = None, text: str = None):
        self.setEnabled(True)
        _icon = QIcon(icon) if icon is not None else QIcon()
        self.setIcon(_icon)
        if text is not None:
            self.setText(text)

    def setMessage(self, msg: str, icon: str = None):
        self.setText(msg)
        if icon is not None:
            self.setIcon(QIcon(icon))

    def setGif(self, file_name: str, text: str = None, dynamic=False) -> None:
        self.setEnabled(False)
        if text:
            self._text = text
            self.setText(text)
        self._dynamic = dynamic
        self.movie = QMovie(file_name)
        self.movie.setSpeed(100)
        # self.movie.setCacheMode() # 设置帧缓存模式
        self.movie.frameChanged.connect(self._update)
        self.movie.start()
        self._start_time = time.time()

    def setIcon(self, icon: QIcon) -> None:
        if self.movie:
            self.movie.stop()
        super().setIcon(icon)

    def stopGif(self) -> None:
        if self.movie:
            self.movie.stop()

    def reStartGif(self) -> None:
        if self.movie:
            self.movie.start()

    def _update(self, index: int) -> None:
        pixmap = self.movie.currentPixmap()
        super().setIcon(QIcon(pixmap))
        if self._dynamic:
            if time.time() - self._start_time >= 0.5:
                if self._text.strip():
                    text = self.text()
                    s = text.strip(self._text)
                    c = len(s)
                    if c == 0:
                        a = self._loading_flag * 1
                    elif c == 1:
                        a = self._loading_flag * 2
                    elif c == 2:
                        a = self._loading_flag * 3
                    elif c == 3:
                        a = ''
                    else:
                        a = ''
                    self.setText(f'{self._text}{a}')
                    self._start_time = time.time()

    def closeEvent(self, event):
        if self.movie:
            self.movie.stop()
        super().closeEvent(event)
