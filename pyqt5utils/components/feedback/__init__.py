from types import MethodType

from typing_extensions import Literal
from typing import Union, Callable

from PyQt5.QtWidgets import (QApplication, QPushButton, QLabel, QWidget, QDialog,
                             QFrame, QGridLayout, QSpacerItem, QSizePolicy, QHBoxLayout,
                             QVBoxLayout)
from PyQt5.QtCore import (QObject, QRectF,
                          Qt, pyqtSignal, QSize, QPropertyAnimation,
                          QEvent, QRect, QPoint, QAbstractAnimation, QSizeF,
                          QPointF, QTimer)
from PyQt5.QtGui import (QPixmap, QIcon, QMovie, QPainter,
                         QColor, QFont, QFontMetrics,
                         QMouseEvent, QPainterPath, QPolygonF, QBitmap)

from pyqt5utils.components import TitleWidget
from .._qt_decorators import addShadow

__all__ = (
    'GifLabel', 'Tips', 'Loading', 'Pop', 'Message', 'Toast', 'Modal', 'Confirm', 'Alerts', 'NoData'
)


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


class Tips(QDialog):

    def __init__(self, content: str = None, parent=None, text_color=None, bk_color=None,
                 place: Literal['l', 't', 'r', 'b'] = 'b', spacing=5):
        super(Tips, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._text = content
        self._x: int = spacing
        self._y: int = spacing
        self._spacing: int = spacing
        self._angle_width = 6
        self._angle_height = 10
        self._font: QFont = QFont('微软雅黑', 8)
        self._text_color = text_color or Qt.lightGray
        self._bk_color = bk_color or QColor('#1B1A19')
        self._place = place
        self._tooltip = False
        self.set_size()
        self.installEventFilter(self)

    def set_size(self):
        fm = QFontMetrics(self._font)
        max_lines = max(self._text.splitlines(), key=lambda e: fm.width(e))
        w = fm.width(max_lines) + self._spacing * 2
        h = len(self._text.splitlines()) * fm.height() + self._spacing * 2 + self._angle_height
        self.setFixedSize(w, h + self._angle_height)
        print('lines; ', len(self._text.splitlines()), self.height())

    def eventFilter(self, a0, a1: QEvent) -> bool:
        if a1.type() == QEvent.WindowDeactivate:
            self.close()
        return QDialog.eventFilter(self, a0, a1)

    def paintEvent(self, a0) -> None:
        super(Tips, self).paintEvent(a0)
        if self._text:
            painter = QPainter(self)
            painter.setRenderHints(QPainter.Antialiasing, True)
            painter.setFont(self._font)
            if self._place == 'b':
                w = self.width() - self._spacing * 2
                h = self.height() - self._spacing * 2 - self._angle_height
                rect = QRect(self._spacing, self._angle_height, w, h)
                path = QPainterPath()
                poly = QPolygonF([
                    QPoint(self._spacing + 6, 0),
                    QPoint(self._spacing + self._x, self._angle_height),
                    QPoint(self._spacing + self._x + self._angle_width, self._angle_height)
                ])
                path.addPolygon(poly)
                path.addRoundedRect(QRectF(rect.adjusted(-self._spacing, 0, self._spacing, 0)), 5, 5)
                painter.fillPath(path, self._bk_color)
                painter.setPen(self._text_color)
                painter.drawText(QRectF(rect.adjusted(0, self._spacing, 0, 0)), self._text)
            elif self._place == 't':
                w = self.width() - self._spacing * 2
                h = self.height() - self._angle_height - self._spacing * 2
                rect = QRect(self._spacing, self._spacing, w, h)
                path = QPainterPath()
                poly = QPolygonF([
                    QPointF(self._spacing + self._x, h + self._spacing * 2),
                    QPointF(self._spacing + self._x + self._angle_width, h + self._spacing * 2),
                    QPointF(self._spacing + self._x + self._angle_width / 3, self.height())
                ])
                path.addPolygon(poly)
                path.addRoundedRect(QRectF(0, 0, w + self._spacing * 2, self.height() - self._angle_height),
                                    5, 5)
                painter.fillPath(path, self._bk_color)
                painter.setPen(self._text_color)
                painter.drawText(QRectF(rect.adjusted(0, self._spacing, 0, -self._spacing)), self._text)

    def _show(self, target: QWidget, target_point: QPoint):
        w, h = target.width(), target.height()
        point = target.mapToGlobal(QPoint(0, h))
        if self._place == 'b':
            p = point + QPoint(-self._spacing, 2) + target_point
        elif self._place == 't':
            p = point + QPoint(-self._spacing, -self.height() - 2 - h) + target_point

        self.move(p)
        self.show()

    @classmethod
    def pop(cls, content: str, target: QWidget, text_color=None, bk_color=None, place='b', spacing=5, dxy: QPoint = QPoint(0, 0)):
        t = cls(content, target, text_color, bk_color, place, spacing)
        t._show(target, dxy)


    @classmethod
    def tooltip(cls, content: str, target: QWidget, text_color=None, bk_color=None, place='b', spacing=5, dxy: QPoint = QPoint(0, 0)):
        t = cls(content, target, text_color, bk_color, place, spacing)
        t._tooltip = True
        t._show(target, dxy)


class Loading(GifLabel):

    def _hook(self, target: QWidget, margin: int):
        def resize_event(this, event):
            ret = this.__class__.resizeEvent(this, event)
            self.setFixedSize(this.size() - QSize(margin * 2, margin * 2))
            self.move(margin, margin)
            return ret

        target.resizeEvent = MethodType(resize_event, target)

    @classmethod
    def load(cls, target: QWidget, margin=0, image: str = None):

        if getattr(target, '__hook_xx_loading__', None) is None:
            self = cls(target)
            self._hook(target, margin)
            self.setAlignment(Qt.AlignCenter)
            self._target = target
            target.__hook_xx_loading__ = self
            self.setFixedSize(target.size() - QSize(margin * 2, margin * 2))
            self.move(margin, margin)
            self.setGif(image or ':/imgs/加载2.gif')
            self.raise_()
            self.show()
        else:
            self = target.__hook_xx_loading__
            self.setFixedSize(target.size())
            self.setGif(image or ':/imgs/加载2.gif')
            self.raise_()
            self.show()

    @classmethod
    def end(cls, target: QWidget):
        if getattr(target, '__hook_xx_loading__', None) is not None:
            target.__hook_xx_loading__.removeGif('')
            target.__hook_xx_loading__.hide()


class Loading2(Loading):

    def _hook(self, target: QWidget, margin: int):
        def resize_event(this, event):
            ret = this.__class__.resizeEvent(this, event)
            self.setFixedWidth(30)
            self.setFixedHeight(min(target.height() - margin * 2, 30))
            # self.move((this.width() - 30) / 2, margin)
            return ret

        target.resizeEvent = MethodType(resize_event, target)

    @classmethod
    def end(cls, target: QWidget):
        target.setEnabled(True)
        if getattr(target, '__hook_xx_loading2__', None) is not None:
            target.__hook_xx_loading2__.removeGif('')
            target.__hook_xx_loading2__.hide()

    @classmethod
    def load(cls, target: QWidget, margin=2):
        if getattr(target, '__hook_xx_loading2__', None) is None:
            self = cls(target)
            self._hook(target, margin)
            self.setAlignment(Qt.AlignCenter)
            self._target = target
            target.__hook_xx_loading2__ = self
            self.setFixedWidth(30)
            self.setFixedHeight(min(target.height() - margin * 2, 30))
            self.move((target.width() - 30) / 2, margin)
            self.setGif(':/imgs/加载2.gif')
            self.setStyleSheet('background: transparent')
            self.raise_()
            self.show()
        else:
            self = target.__hook_xx_loading2__
            self.setFixedWidth(30)
            self.setFixedHeight(min(target.height() - margin * 2, 30))
            self.setGif(':/imgs/加载2.gif')
            self.raise_()
            self.show()
        target.setEnabled(False)


class LoadingCenter(Loading):

    def _hook(self, target: QWidget, margin: int):
        def resize_event(this, event):
            ret = this.__class__.resizeEvent(this, event)
            self.setFixedWidth(30)
            self.setFixedHeight(min(target.height() - margin * 2, 30))
            self.move((this.width() - 30) / 2, (this.height() - self.height()) / 2)
            return ret

        target.resizeEvent = MethodType(resize_event, target)

    @classmethod
    def end(cls, target: QWidget):
        target.setEnabled(True)
        if getattr(target, '__hook_xx_loading3__', None) is not None:
            target.__hook_xx_loading3__.removeGif('')
            target.__hook_xx_loading3__.hide()

    @classmethod
    def load(cls, target: QWidget, margin=2):
        if getattr(target, '__hook_xx_loading2__', None) is None:
            self = cls(target)
            self._hook(target, margin)
            self.setAlignment(Qt.AlignCenter)
            self._target = target
            target.__hook_xx_loading3__ = self
            self.setFixedWidth(30)
            self.setFixedHeight(min(target.height() - margin * 2, 30))
            self.move((target.width() - 30) / 2, (target.height() - self.height()) / 2)
            self.setGif(':/imgs/加载2.gif')
            self.setStyleSheet('background: transparent')
            self.raise_()
            self.show()
        else:
            self = target.__hook_xx_loading3__
            self.setFixedWidth(30)
            self.setFixedHeight(min(target.height() - margin * 2, 30))
            self.setGif(':/imgs/加载2.gif')
            self.raise_()
            self.show()
            self.move((target.width() - 30) / 2, (target.height() - self.height()) / 2)
        target.setEnabled(False)


class Pop(QPushButton):
    thread_sig = pyqtSignal(str)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.setStyleSheet(
            'QPushButton{background:#B6B6B6;color:white; border: 1px solid #B6B6B6;border-radius:5px;font-family: 微软雅黑}')
        fm = self.fontMetrics()
        self.setFixedHeight(fm.height() * 2.5)
        self._close_flag = False
        self._time_id = None

    def _hook(self, target: QWidget):
        def resize_event(this, event):
            ret = this.__class__.resizeEvent(this, event)
            target_size = this.size()
            pop_size = self.size()
            delta = (target_size - pop_size) / 2
            self.move(delta.width(), delta.height())
            return ret

        target.resizeEvent = MethodType(resize_event, target)

    def timerEvent(self, e) -> None:
        ret = super().timerEvent(e)
        if self._time_id is not None:
            self.killTimer(self._time_id)
            self._time_id = None
        self.close()
        return ret

    @classmethod
    def display(cls, text: str, target: QWidget, timeout: int = 5000):

        if getattr(target, '__hook_xx_pop__', None) is None:
            self = cls(target)
            self._hook(target)
            self.setText(text)
            fm = self.fontMetrics()
            self._target = target
            target.__hook_xx_pop__ = self
            self.setFixedWidth(fm.width(self.text()) + 20)
            self.setFixedHeight(fm.height() * 2.5)
            delta = (target.size() - self.size()) / 2
            self.move(delta.width(), delta.height())
            self.raise_()
            self.show()
            self._time_id = self.startTimer(timeout)

        else:
            self = target.__hook_xx_pop__
            if self._time_id is not None:
                self.killTimer(self._time_id)
            self.raise_()
            self.show()
            self._time_id = self.startTimer(timeout)

    @classmethod
    def end(cls, target: QWidget):
        if getattr(target, '__hook_xx_pop__', None) is not None:
            target.__hook_xx_pop__.hide()


# @addShadow
class Message(QDialog):
    _instances = set()

    def _get_mask(self, radius=5) -> QBitmap:
        bitmap = QBitmap(self.size())
        bitmap.fill(Qt.color0)
        painter = QPainter(bitmap)
        # painter.setRenderHint(QPainter.Antialiasing, True)
        # painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing,
                               True)
        painter.setPen(Qt.transparent)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        painter.fillPath(path, Qt.color1)
        return bitmap

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.icon_label = QPushButton()
        self.icon_label.setStyleSheet("border:none")
        self.icon_label.setFixedWidth(18)
        self.icon_label.setFixedHeight(18)

        self.top_lay = QVBoxLayout(self)
        self.top_lay.setContentsMargins(1, 1, 1, 1)

        self.label = QLabel()
        self.label.setStyleSheet("border:none;font-family:微软雅黑")
        self.label.setAlignment(Qt.AlignCenter)
        self._timer = None

        frame = QFrame()
        frame.setStyleSheet('border:none')

        lay = QHBoxLayout(frame)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.addWidget(self.icon_label, 0)
        lay.addWidget(self.label, 1)

        desktop = QApplication.desktop()
        fm = self.label.fontMetrics()
        label_height = fm.height()
        self.label.setFixedHeight(label_height)
        self._w = desktop.width()
        self._call_back = None

        self.top_lay.addWidget(frame)

        self.setStyleSheet(
            "border: 1px solid lightgray;border-radius: 5px; background-color:white"
        )

    def _add_confirm(self):
        frame = QFrame()
        frame_lay = QHBoxLayout(frame)
        frame_lay.setContentsMargins(20, 0, 5, 0)
        frame_lay.addSpacerItem(QSpacerItem(2000, 20, hPolicy=QSizePolicy.Expanding))
        frame.setStyleSheet('border:none')
        btn = QPushButton()
        btn.setText('确认')
        btn.setStyleSheet(
            'QPushButton{font-family:微软雅黑;background: #40A9FF;color:white;border:1px solid #40A9FF;border-radius:3px;padding: 3px}'
            'QPushButton:hover{background: rgb(24,144,255);border:1px solid rgb(24,144,255)}')
        frame_lay.addWidget(btn)
        # frame_lay.addSpacerItem(QSpacerItem(2000, 20, hPolicy=QSizePolicy.Expanding))
        btn.clicked.connect(self.close)
        self.top_lay.addWidget(frame)

    def fwidth(self, msg: str):
        fm = self.label.fontMetrics()
        width = fm.width(msg)
        return width + 40 + self.icon_label.width()

    def _show(self, type: Literal["show", "exec_"] = "show", target: QWidget = None, center=None, moved=True):
        height = self.height()
        count = len(self._instances)
        padding = 4
        self._instances.add(self)
        show_height = height * count + padding * count
        if target is not None:
            if self.parent():
                if getattr(self, '__shadialog_hook__', None) is None:
                    w = (self.parent().width() - self.width()) / 2
                else:
                    w = (self.parent().width() - self.width()) / 2
                    # target_point = target.mapToGlobal(QPoint(0, 0))
                    # if self.width() < target.width():
                    #     del_size = target.size() - self.size()
                    #     dw, dh = del_size.width(), del_size.height()
                    #     w = target_point.x() + dw / 2
                    #     show_height = target_point.y() + 10
                self.move(w, show_height)
            self.raise_()
            if type == "show":
                self.show()
            else:
                self.exec_()
        else:
            desk = QApplication.desktop().size()
            size = self.size()
            s = (desk - size) / 2
            if center is None:
                h = 15 + show_height
            elif center is True:
                h = s.height()
            elif isinstance(center, (int, float)):
                h = int(center) + show_height
            if moved:
                self.move(s.width(), h)
            self.setMask(self._get_mask())
            self.raise_()
            self.show()

    def timerEvent(self, a0: "QTimerEvent") -> None:
        super().timerEvent(a0)
        if self._timer is not None:
            self.killTimer(self._timer)
            self.close()

    def close(self) -> bool:
        super().close()
        try:
            self._instances.remove(self)
        except:
            pass
        if self._call_back:
            self._call_back()

    @classmethod
    def info(cls, msg: str, target: QWidget = None, duration: int = 1500, type: Literal["show", "exec_"] = "show",
             center: Union[bool, int] = None):
        w = cls(target)
        icon = QIcon(":/imgs/成功.svg")
        h = w.label.height() + 20
        icon_size = (h - 20) + 4
        w.icon_label.setIcon(icon)
        w.icon_label.setIconSize(QSize(icon_size, icon_size))
        w.icon_label.setFixedSize(QSize(icon_size, icon_size))
        w.label.setText(msg)
        w.setFixedWidth(w.fwidth(msg))
        w.setFixedHeight(h)
        w._timer = w.startTimer(duration)
        w._show(type, target, center)

    @classmethod
    def warn(cls, msg: str, target: QWidget = None, duration: int = 1500, type: Literal["show", "exec_"] = "show",
             call_back=None, center: Union[bool, int] = None, rich=False):
        w = cls(target)
        w._call_back = call_back
        icon = QIcon(":/imgs/失败.svg")
        h = w.label.height() + 20
        icon_size = (h - 20) + 4
        w.icon_label.setIcon(icon)
        w.icon_label.setIconSize(QSize(icon_size, icon_size))
        w.icon_label.setFixedSize(QSize(icon_size, icon_size))
        if rich:
            lines = msg.split(r'\n')
            max_lines = [w.fwidth(line) for line in lines]
            lines_count = len(lines)
            w.label.setAlignment(Qt.AlignTop)
            data = '<br>'.join(lines)
            w.setFixedWidth(max(max_lines))
            w.setFixedHeight(h * lines_count)
            w.label.setFixedHeight(w.label.height() * lines_count)
            w.label.setText(data)
        else:
            w.label.setText(msg)
            w.setFixedWidth(w.fwidth(msg))
            w.setFixedHeight(h)

        w._timer = w.startTimer(duration)
        w._show(type, target, center)

    @classmethod
    def confirm(cls, msg: str, target: QWidget, center=None):
        w = cls()
        w.layout().setContentsMargins(1, 5, 1, 5)
        w.setWindowFlags(w.windowFlags() | Qt.Dialog)
        w._add_confirm()
        icon = QIcon(":/imgs/失败.svg")
        h = w.label.height() + 20
        icon_size = (h - 20) + 4
        w.icon_label.setIcon(icon)
        w.icon_label.setIconSize(QSize(icon_size, icon_size))
        w.icon_label.setFixedSize(QSize(icon_size, icon_size))
        w.label.setText(msg)
        w.setFixedWidth(w.fwidth(msg))
        w.setFixedHeight(h * 2)

        left = target.mapToGlobal(QPoint(0, 0))
        size = target.size()
        s = (size - w.size()) / 2
        w.move(left.x() + s.width(), left.y() + 50)
        w._show('exec_', target, center, moved=False)


class Toast(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._font = QFont('微软雅黑', 9)
        self._text = None
        self._target = None
        self._max_width = 100
        self._padding = 10
        self._back_color = QColor('#404040')
        self._text_color = QColor(Qt.white)

        self._cursor_x = None
        self._place = 't'
        self._cursor_w = 10
        self._cursor_h = 5

        self._keep = False
        self._any_leave = True

        self.installEventFilter(self)

    def _text_height(self, text: str):
        fm = QFontMetrics(self._font)
        lines = []
        k = 0
        length = len(text)
        raw = text
        for index, i in enumerate(range(length)):
            l = text[:i - k]
            if fm.width(l) <= self._max_width:
                pass
            else:
                lines.append(''.join(l))
                text = text[i - k:]
                k = len(l)
        l = len(lines)
        last = raw.replace(''.join(lines), '')
        lines.append(last)
        return l, lines

    def eventFilter(self, a0, a1) -> bool:
        if a1.type() == QEvent.WindowDeactivate:
            if not self._keep:
                if self._target is not None:
                    try:
                        delattr(self._target, '__0xxxmake_text_from_toastxxx0__')
                    except:
                        pass
                self.close()
                return True
        if self._any_leave:
            if a1.type() == QEvent.KeyPress:
                if not self._keep:
                    if self._target is not None:
                        try:
                            delattr(self._target, '__0xxxmake_text_from_toastxxx0__')
                        except:
                            pass
                    self.close()
                    return True
        return QDialog.eventFilter(self, a0, a1)

    def paintEvent(self, a0: 'QPaintEvent') -> None:
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.TextAntialiasing, True)
        painter.setPen(self._back_color)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height() - 5, 3, 3)

        x1 = QPoint(self.width() / 2 - 5, self.height() - 5)
        x2 = QPoint(self.width() / 2 + 5, self.height() - 5)
        x3 = QPoint(self.width() / 2, self.height())
        path.addPolygon(QPolygonF([x1, x2, x3]))

        painter.fillPath(path, self._back_color)

    def set_text(self, st: str):
        pass

    def set_keep(self, v: bool):
        self._keep = v

    def set_any_release(self, v: bool):
        self._any_leave = v

    @classmethod
    def make_text(cls, text: str, target: QWidget,
                  text_color=None, back_color=None,
                  width: int = 100, place: Literal['l', 'r', 't', 'b'] = 't',
                  keep=False):

        self = cls()
        self._keep = keep
        self._max_width = width
        self._place = place
        fm = QFontMetrics(self._font)

        if self._max_width is None:
            self._max_width = fm.width(text)
        size, lines = self._text_height(text.strip())

        if text_color is not None:
            self._text_color = QColor(text_color)
        if back_color is not None:
            self._back_color = QColor(back_color)

        self.label = QLabel(self)
        # self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setFont(self._font)
        self.label.setStyleSheet(
            f'border:none;background:transparent;color: {self._text_color.name()};')

        self._text = '\n'.join(lines)

        height = fm.height() * (size + max(0, text.strip().count('\n') - 1)) + fm.lineSpacing()
        width = self._max_width + self._padding * 2 + 2

        self.setFixedWidth(width + fm.width(' ') * 1.5)
        self.setFixedHeight(height + self._padding * 2 + 5)

        self.label.move(self._padding, self._padding)
        self.label.setFixedWidth(self.width() - self._padding * 2)
        self.label.setFixedHeight(self.height() - self._padding * 2 - 5)
        self.label.setText(''.join(lines))
        self.label.setWordWrap(True)

        self._target = target
        setattr(target, '__0xxxmake_text_from_toastxxx0__', self)
        p1 = target.mapToGlobal(QPoint(target.width() / 2, 0))
        self.move(p1 - QPoint(self.width() / 2, self.height()))
        self.raise_()
        self.show()
        return self


class Modal(object):
    # 遮罩颜色
    mask_color = QColor(200, 200, 200, 70)

    @classmethod
    def _hook_parent(cls, obj: QWidget):
        def add_shadow(pixmap: QPixmap):
            painter = QPainter()
            painter.begin(pixmap)
            painter.fillRect(pixmap.rect(), cls.mask_color)
            painter.end()

        def _leave_focus(this):
            pixmap = this.grab()
            add_shadow(pixmap)
            this.__focus_label__.setFixedSize(pixmap.size())
            this.__focus_label__.setPixmap(pixmap)
            this.__focus_label__.raise_()
            this.__focus_label__.show()

        def _in_focus(this):
            this.__focus_label__.hide()

        # 遮罩绘制
        label = QLabel(obj)
        label.setStyleSheet('border:none')
        label.hide()
        obj.__focus_label__ = label
        obj._leave_focus = MethodType(_leave_focus, obj)
        obj._in_focus = MethodType(_in_focus, obj)

    @classmethod
    def _hook_modal(cls, obj: QWidget):
        def closeEvent(this, event):
            this.__class__.closeEvent(this, event)
            this.parent()._in_focus()

        obj.closeEvent = MethodType(closeEvent, obj)

    @classmethod
    def show(cls, title: str, show_content: QWidget, parent: QWidget,
             bar_color=QColor('#426BDD'),
             text_color=Qt.white,
             back_color=Qt.white,
             center=True):
        t = TitleWidget(title, show_content, bar_color, parent)
        cls._hook_modal(t)
        cls._hook_parent(parent)

        t.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        t.setWindowModality(Qt.WindowModal)
        t.setTextColor(text_color)
        t.hide_titlebar_all()
        btn = t.close_btn(
            'QPushButton{color:%s;border:none;background:transparent}' % QColor(text_color).name())
        t.addTitleWidget(btn)
        t.resize(show_content.size())
        t.setStyleSheet('TitleWidget{background:%s}' %
                        QColor(back_color).name())
        parent._leave_focus()
        if center:
            desk = QApplication.desktop().size()
            si = show_content.size()
            x = (desk - si) / 2
            t.move(QPoint(x.width(), x.height()))
        else:
            p = parent.mapToGlobal(QPoint(0, 0))
            t
        t.show()


@addShadow
class Confirm(QDialog):

    @classmethod
    def msg(cls, title: str, target: QWidget, content: QWidget = None,
            ok: Callable = None, cancel: Callable = None,
            ok_condition: Callable = None, cancel_condition: Callable = None,
            image: str = None, rich=False, after_close=None, after_close_duration=None):
        def _wrapper_ok():
            if ok:
                if ok_condition is not None:
                    val, msg = ok_condition(content)
                    if val:
                        flag_ = True
                    else:
                        flag_ = False
                else:
                    flag_ = True
                if flag_:
                    ret = ok()
                    if ret is None:
                        dia.close()
                        if timer:
                            timer.start(after_close_duration or 100)
                    else:
                        if ret:
                            dia.close()
                            if timer:
                                timer.start(after_close_duration or 100)
                else:
                    Message.warn(msg, dia)

            else:
                dia.close()
                if timer:
                    timer.start(after_close_duration or 100)

        def _wrapper_cancel():
            if cancel:
                if cancel_condition is not None:
                    val, msg = cancel_condition(content)
                    if val:
                        flag_ = True
                    else:
                        flag_ = False
                else:
                    flag_ = True
                if flag_:
                    ret = cancel()
                    if ret is None:
                        dia.close()
                    else:
                        if ret:
                            dia.close()
                else:
                    Message.warn(msg, dia)
            else:
                dia.close()

        if after_close:
            def _close():
                after_close()
                timer.stop()

            timer = QTimer()
            timer.timeout.connect(_close)
        else:
            timer = None

        dia = cls(target)
        dia.setObjectName('ConfirmObject')
        dia.setStyleSheet('QFrame{background: transparent} #ConfirmObject{background:transparent}')

        lay = QVBoxLayout(dia)
        lay.setSpacing(0)
        frame = QFrame()
        f_lay = QHBoxLayout(frame)
        info_btn = QPushButton()
        info_btn.setStyleSheet('border:none;background: transparent')
        info_btn.setIcon(QIcon(':/new/问号2.svg' if image is None else image))
        info_btn.setIconSize(QSize(25, 25))
        f_lay.addWidget(info_btn, 0)
        info_label = QLabel()
        info_label.setWordWrap(True)
        info_label.setStyleSheet('QLabel{border:none;font-family: 微软雅黑;color:black}')
        f_lay.addWidget(info_label, 1)
        if rich:
            # parse \n
            lines = title.split(r'\n')
            info_label.setAlignment(Qt.AlignTop)
            data = '<br>'.join(lines)
            info_label.setText(data)
        else:
            info_label.setText(title)
        btn_frames = QFrame()
        btn_lay = QHBoxLayout(btn_frames)
        btn_lay.addSpacerItem(QSpacerItem(
            20000, 20, hPolicy=QSizePolicy.Expanding))

        ok_btn = QPushButton('确认', clicked=_wrapper_ok)
        cancel_btn = QPushButton('取消', clicked=_wrapper_cancel)
        ok_btn.setStyleSheet(
            'QPushButton{font-family:微软雅黑;background: #40A9FF;color:white;border:1px solid #40A9FF;border-radius:3px;'
            'padding:2px 8px}'
            'QPushButton:hover{background: rgb(24,144,255);border:1px solid rgb(24,144,255)}')
        cancel_btn.setStyleSheet(
            'QPushButton{font-family: 微软雅黑; background: white;border:1px solid lightgray;border-radius:3px;color:black;'
            'padding:2px 8px}'
            'QPushButton:hover{background: #F5F5F5}')

        ok_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        fb = ok_btn.fontMetrics().height()
        ok_btn.setMaximumHeight(fb + 10)
        cancel_btn.setMaximumHeight(fb + 10)

        btn_lay.addWidget(cancel_btn)
        btn_lay.addWidget(ok_btn)

        lay.addWidget(frame, 1)
        if content:
            lay.addWidget(content, 100)
        lay.addWidget(btn_frames, 0)
        flag = (target.size() - dia.size()) / 2

        dia.setMaximumWidth(350)
        dia.exec_()
        dia.move(flag.width(), flag.height())

    @classmethod
    def warn(cls, title: str, target: QWidget, content: QWidget = None, ok=None, cancel=None):
        return cls.msg(title, target, content, ok, cancel)

    @classmethod
    def info(cls, title: str, target: QWidget, content: QWidget = None, ok=None, cancel=None):
        cls.msg(title, target, content, ok, cancel, image=':/imgs/成功.svg')


class Alerts(QDialog):

    def __init__(self, target: QWidget = None) -> None:
        super().__init__(target)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Dialog | Qt.WindowStaysOnTopHint)
        lay = QGridLayout(self)

        icon = QPushButton()
        icon.setStyleSheet('border:none;background:transparent')
        icon.setIcon(QIcon(':/feedback/警告 (2).svg'))
        lay.addWidget(icon, 0, 0)

        title = QLabel()
        title.setStyleSheet('font-family:微软雅黑;font-weight:bold')
        lay.addWidget(title, 0, 1)

        content = QLabel()
        content.setStyleSheet('font-family:微软雅黑;color: gray')
        lay.addWidget(content, 1, 1)

        self.title_label = title
        self.content_label = content
        self.icon = icon

        self.setMaximumWidth(300)
        self.time_id = None

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        ret = super().timerEvent(a0)
        if self.time_id is not None:
            self.killTimer(self.time_id)
            self.close()

    @classmethod
    def info(cls, title: str, content: str, target: QWidget = None, duration=3000):
        dialog = cls(target)
        dialog.setStyleSheet(
            'QDialog{border:1px solid #91D5FF;background: #E6F7FF;border-radius:3px}')
        dialog.title_label.setText(title)
        dialog.content_label.setText(content)
        dialog.time_id = dialog.startTimer(duration)
        dialog.raise_()
        dialog.exec_()

    @classmethod
    def warn(cls, title: str, content: str, target: QWidget = None, duration=3000):
        dialog = cls(target)
        dialog.icon.setIcon(QIcon(':/feedback/警告 (3).svg'))
        dialog.setStyleSheet(
            'QDialog{border:1px solid #FFE58F;background: #FFFBE6;border-radius:3px}')
        dialog.title_label.setText(title)
        dialog.content_label.setText(content)
        dialog.time_id = dialog.startTimer(duration)
        dialog.raise_()
        dialog.exec_()

    @classmethod
    def error(cls, title: str, content: str, target: QWidget = None, duration=3000):
        dialog = cls(target)
        dialog.icon.setIcon(QIcon(':/feedback/警告-红.svg'))
        dialog.setStyleSheet(
            'QDialog{border:1px solid #FFA39E;background: #FFF1F0;border-radius:3px}')
        dialog.title_label.setText(title)
        dialog.content_label.setText(content)
        dialog.time_id = dialog.startTimer(duration)
        dialog.raise_()
        dialog.exec_()


class NoData(QWidget):
    def __init__(self, picture: str = None, text: str = None, parent=None, size: QSize = None):
        super(NoData, self).__init__(parent)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.addSpacerItem(QSpacerItem(40, 40, vPolicy=QSizePolicy.Expanding))
        frame = QFrame()
        frame_lay = QHBoxLayout(frame)
        frame_lay.addSpacerItem(QSpacerItem(40, 40, hPolicy=QSizePolicy.Expanding))
        self._label = QLabel(self)
        self._label.setScaledContents(True)
        self._label.setAlignment(Qt.AlignVCenter)
        self._label.setPixmap(
            QPixmap(picture or ':/imgs/缺省页_暂无数据.svg'))  # .scaled(60, 60, transformMode=Qt.SmoothTransformation))
        self._label.setMaximumSize(size or QSize(100, 100))
        frame_lay.addWidget(self._label)
        frame_lay.addSpacerItem(QSpacerItem(40, 40, hPolicy=QSizePolicy.Expanding))
        self._lay.addWidget(frame)

        label = QLabel(text or '暂无数据')
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet('font-family: 微软雅黑')
        self._lay.addWidget(label)
        self._lay.addSpacerItem(QSpacerItem(40, 40, vPolicy=QSizePolicy.Expanding))

    @classmethod
    def display(cls, target: QWidget, image: str = None, text: str = None, pic_size: QSize = None):
        def hook(this, event):
            this.__class__.resizeEvent(this, event)
            instance.setFixedSize(target.size())

        if getattr(target, '__hook_no_data__', None) is None:
            instance = cls(image, parent=target, text=text, size=pic_size)
            instance.raise_()
            instance.show()
            instance.setFixedSize(target.size())
            target.__hook_no_data__ = instance
            target.resizeEvent = MethodType(hook, target)
        else:
            target.__hook_no_data__.raise_()
            target.__hook_no_data__.show()
            target.__hook_no_data__.setFixedSize(target.size())

    @classmethod
    def end(cls, target: QWidget):
        if getattr(target, '__hook_no_data__', None) is not None:
            target.__hook_no_data__.hide()
