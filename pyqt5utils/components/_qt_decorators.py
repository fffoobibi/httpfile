from enum import IntEnum
from functools import wraps, partial
from typing import Type, Union

from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QPoint, QPointF
from PyQt5.QtWidgets import QWidget, QPushButton, QDialog, QVBoxLayout, QGraphicsDropShadowEffect

from .frameless import TitleWidget

__all__ = ('color_widget', 'addSideButton', 'addScrollBarHidePolicy')


def _hook_qt_widget(target: Type[QWidget]):
    assert issubclass(target, QWidget)

    def wrapper(func):
        @wraps(func)
        def inner(self, *a, **kw):
            ret = old(self, *a, **kw)
            func(self, *a, **kw)
            return ret

        if hasattr(target, func.__name__):
            old = getattr(target, func.__name__)
            setattr(target, func.__name__, inner)
        # return inner

    return wrapper


def color_widget(title='',
                 bar_color=QColor('#426BDD'),
                 border_color=Qt.gray,
                 text_color=Qt.white,
                 auto_resize=False,
                 nestle_enable=False,
                 icon: str = None,
                 icon_size: int = 16,
                 button_text_color=Qt.white,
                 button_hover_color=QColor(109, 139, 222),
                 button_hide_policy: set = None,
                 back_ground_color: Union[str, QColor] = None,
                 bar_height: int = None):
    def wrapper_init(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            func(self, *args, **kwargs)
            TitleWidget(title,
                        widget=self,
                        bar_height=bar_height,
                        back_ground_color=back_ground_color,
                        bar_color=bar_color,
                        border_color=border_color,
                        text_color=text_color,
                        auto_resize=auto_resize,
                        nestle_enable=nestle_enable,
                        icon=icon,
                        icon_size=icon_size,
                        button_text_color=button_text_color,
                        button_hover_color=button_hover_color,
                        button_hide_policy=button_hide_policy,
                        )
            self.setWindowTitle(title or self.windowTitle())
            self.setAutoFillBackground(True)
            pale = self.palette()
            pale.setColor(QPalette.Window, Qt.transparent)
            self.setPalette(pale)

        return inner

    def wrapper(cls) -> Type[QWidget]:
        cls.__init__ = wrapper_init(cls.__init__)
        cls._decorated_by_title = True
        return cls

    return wrapper


class Place(IntEnum):
    top_left = 0
    top_right = 1
    center_left = 2
    center_right = 3
    bottom_left = 4
    bottom_right = 5


def addSideButton(cls: Type[QWidget] = None, place: Place = Place.center_left):
    if cls is None:
        return partial(addSideButton, place=place)
    assert issubclass(cls, QWidget)

    @_hook_qt_widget(cls)
    def __init__(self, *a, **kw):
        self.__add_tab = QPushButton('>', self)
        self.__add_tab.setCheckable(True)
        self.__add_tab.setFixedSize(QSize(12, 80))
        self.__add_tab.clicked[bool].connect(self.sideButtonClick)
        self.__add_tab.setStyleSheet('QPushButton{padding:0px;border-radius:3px;border:1px solid lightgray}'
                                     'QPushButton:hover{background: lightgray} ')
        self.__add_tab.raise_()
        self.__add_tab.show()

    @_hook_qt_widget(cls)
    def resizeEvent(self, event):
        move_policy(self, place)
        self.__add_tab.raise_()
        self.__add_tab.show()

    @_hook_qt_widget(cls)
    def enterEvent(self, event):
        self.__add_tab.raise_()
        self.__add_tab.show()

    @_hook_qt_widget(cls)
    def leaveEvent(self, event):
        self.__add_tab.hide()

    def move_policy(self, _place: Place):
        target = self.size()
        size = self.__add_tab.size()
        if _place == Place.center_left:
            self.__add_tab.move(0, (target - size).height() / 2)
        elif _place == Place.center_right:
            self.__add_tab.move((target - size).width(),
                                (target - size).height() / 2)
        elif _place == Place.top_left:
            self.__add_tab.move(0, 0)
        elif _place == Place.top_right:
            self.__add_tab.move((target - size).width(), 0)
        elif _place == Place.bottom_left:
            self.__add_tab.move(0, (target - size).height())
        elif _place == Place.bottom_right:
            self.__add_tab.move((target - size).width(),
                                (target - size).height())

    def sideButtonClick(self, checked):
        import warnings
        warnings.warn('Implement `sideButtonClick(bool)` method')

    def wrapper_side_slot(func):
        @wraps(func)
        def inner(self, checked):
            ret = func(self, checked)
            if checked:
                self.__add_tab.setText('<')
            else:
                self.__add_tab.setText('>')
            return ret

        return inner

    if not hasattr(cls, 'sideButtonClick'):
        cls.sideButtonClick = wrapper_side_slot(sideButtonClick)
    else:
        cls.sideButtonClick = wrapper_side_slot(cls.sideButtonClick)
    return cls


def addScrollBarHidePolicy(cls: Type[QWidget]):
    assert issubclass(cls, QWidget)
    assert hasattr(cls, 'verticalScrollBar')

    def animation(self):
        self.__animation.setStartValue(self.verticalScrollBar().value())
        self.__animation.setEndValue(0)
        self.__animation.start()

    def policy(self, value):
        total = self.verticalScrollBar().maximum() - self.verticalScrollBar().minimum() + 1
        if value / total > 0.1:
            size = self.size()
            if self.__move_btn.isHidden():
                s = self.__move_btn.size()
                self.__move_btn.move(
                    size.width() - 12 - s.width(), size.height() - 12 - s.height())
                self.__move_btn.raise_()
                self.__move_btn.show()
        else:
            self.__move_btn.hide()

    @_hook_qt_widget(cls)
    def __init__(self, *a, **kw):
        size = 28
        self.__move_btn = QPushButton(self)
        self.__move_btn.setStyleSheet(
            'QPushButton{border-radius:150px; background: transparent;image:url(:/other/向上箭头-深.svg)}'
            'QPushButton:hover{border-radius:150px;image: url(:/other/向上箭头.svg);background: transparent;}')
        self.__move_btn.setFixedSize(size, size)
        self.__move_btn.setCursor(Qt.PointingHandCursor)
        self.__move_btn.hide()
        self.verticalScrollBar().hide()

        self.__animation = QPropertyAnimation(self, b'')
        self.__animation.setDuration(200)
        self.verticalScrollBar().valueChanged.connect(lambda value: policy(self, value))
        self.__animation.valueChanged.connect(
            lambda v: self.verticalScrollBar().setValue(v))
        self.__move_btn.clicked.connect(lambda: animation(self))

    @_hook_qt_widget(cls)
    def enterEvent(self, event):
        self.verticalScrollBar().show()
        total = self.verticalScrollBar().maximum() - self.verticalScrollBar().minimum() + 1
        current = self.verticalScrollBar().value()
        if current / total > 0.5:
            size = self.size()
            s = self.__move_btn.size()
            self.__move_btn.move(size.width() - 12 - s.width(),
                                 size.height() - 12 - s.height())
            self.__move_btn.raise_()
            self.__move_btn.show()

    @_hook_qt_widget(cls)
    def leaveEvent(self, event):
        self.verticalScrollBar().hide()
        self.__move_btn.hide()

    return cls


def addShadow(cls: Type[QWidget]):
    assert issubclass(cls, QWidget)

    @_hook_qt_widget(cls)
    def __init__(this, *a, **kw):
        self = QDialog(this.parent())
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._spacing = 5

        lay = QVBoxLayout(self)
        lay.setContentsMargins(self._spacing, self._spacing, self._spacing, self._spacing)

        self.frame_less = QWidget()
        self.frame_less.setObjectName('FrameLess')
        self.frame_less.setStyleSheet(
            '#FrameLess{background:white;color:black;font-family:微软雅黑;border-radius:5px;border:none}')
        lay.addWidget(self.frame_less)

        self._lay = QVBoxLayout(self.frame_less)
        self._lay.setContentsMargins(5, 5, 5, 5)

        # shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.gray)
        shadow.setBlurRadius(10)
        self.frame_less.setGraphicsEffect(shadow)
        self._lay.addWidget(this)
        this.__shadialog_hook__ = self
        print('shadow: ', self.parent())

    @_hook_qt_widget(cls)
    def setMaximumWidth(self, width):
        spacing = self.__shadialog_hook__._spacing
        self.__shadialog_hook__.setMaximumWidth(width + spacing * 2)

    @_hook_qt_widget(cls)
    def setMaximumHeight(self, height):
        spacing = self.__shadialog_hook__._spacing
        self.__shadialog_hook__.setMaximumHeight(height + spacing * 2)

    def exec_(self):
        self.__shadialog_hook__.exec_()

    def move(self, p1, p2=None):
        if isinstance(p1, (QPoint, QPointF)):
            self.__shadialog_hook__.move(p1)
        else:
            self.__shadialog_hook__.move(p1, p2)

    def close(self):
        self.__shadialog_hook__.close()

    def raise_(self):
        self.__shadialog_hook__.raise_()

    def show(self):
        self.__shadialog_hook__.show()

    def setHidden(self, value):
        # self.__shadialog_hook__.setHidden = value
        self.__shadialog_hook__.setHidden(value)

    def isHidden(self):
        return self.__shadialog_hook__.isHidden()

    cls.close = close
    cls.move = move
    cls.raise_ = raise_
    cls.show = show
    cls.setHidden = setHidden
    cls.isHidden = isHidden
    if hasattr(cls, 'exec_'):
        cls.exec_ = exec_
    return cls
