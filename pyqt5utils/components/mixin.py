# -*- coding: utf-8 -*-
# @Time    : 2022/10/24 8:26
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : mixin.py
# @Software: PyCharm
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QWidget
from functools import wraps

from pyqt5utils.components import TitleWidget


def _after(clz, func_name):
    def decorator(func):
        @wraps(func)
        def inner(self, *a, **kw):
            getattr(clz, f'__old_{func_name}')(self, *a, **kw)
            ret = func(self, *a, **kw)
            return ret

        setattr(clz, f'__old_{func_name}', getattr(clz, func_name))
        return inner

    return decorator


def close(self):
    try:
        self._instance.remove(self)
    except Exception:
        pass


def __init__(self, *a, **kw):
    self.keep_ref()


class KeepAliveAndCloseMixIn(object):
    _instance = set()

    def __init_subclass__(cls, **kwargs):
        assert issubclass(cls, QWidget)
        cls.close = _after(cls, 'close')(close)
        cls.__init__ = _after(cls, '__init__')(__init__)

    def keep_ref(self):
        self._instance.add(self)


class DragMoveMixin(object):
    pass


class KeepMoveTogetherMixIn(object):
    _keep_together_enable = False

    def set_together_enable(self, val: bool):
        self._keep_together_enable = val

    def set_together_target(self, target: QWidget):
        if hasattr(target, 'windowMoved'):
            target.windowMoved.connect(self.__move_together)
            self.__keep_target = target
            return
        if hasattr(target, '_decorated_by_title'):
            target.root.windowMoved.connect(self.__move_together)
            self.__keep_target = target
            return
        if hasattr(target, 'root') and isinstance(target.root, TitleWidget):
            target.root.windowMoved.connect(self.__move_together)
            self.__keep_target = target
            return

    def __move_together(self, point: QPoint):
        if self._keep_together_enable:
            if not hasattr(self, '_keep_delta'):
                self._keep_delta: QPoint = self.mapToGlobal(QPoint(0, 0)) - self.__keep_target.root.mapToGlobal(QPoint(0, 0))
                self._keep_delta.setY(self._keep_delta.y() + 2)  # spacing 2
            self.move(point + self._keep_delta)
            self.raise_()


__all__ = (
    'KeepAliveAndCloseMixIn',
    'KeepMoveTogetherMixIn'
)
