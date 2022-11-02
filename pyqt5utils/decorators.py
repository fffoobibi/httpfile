import threading
import typing
import warnings

from typing import Type
from pyqt5utils._types import SingletonType

from pyqt5utils.components._qt_decorators import color_widget, addSideButton, addScrollBarHidePolicy, addShadow

__all__ = ('deprecated', 'singleton', 'color_widget', 'addSideButton', 'addScrollBarHidePolicy', 'addShadow', 'cached_property')


def deprecated(func):
    warnings.warn('函数过期，不推荐使用', DeprecationWarning)
    return func


T = typing.TypeVar('T')


def singleton(cls: Type[T]) -> Type[T]:
    instances = {}
    lock = threading.Lock()
    _old = cls.__new__
    _old_init = cls.__init__
    _init_flag = False

    @classmethod
    def __new__(cl, *a, **kw):
        with lock:
            if cls not in instances:
                ret = _old(*a, **kw)
                instances[cls] = ret
        return instances[cls]

    def __init__(self, *a, **kw):
        nonlocal _init_flag
        with lock:
            if _init_flag is False:
                _old_init(self, *a, **kw)
                _init_flag = True

    cls.__init__ = __init__
    cls.__new__ = __new__
    SingletonType.register(cls)
    return cls


# todo
def must_call(func):
    pass


class cached_property(object):
    """
    stolen from django
    """
    name = None

    @staticmethod
    def func(instance):
        raise TypeError(
            'Cannot use cached_property instance without calling '
            '__set_name__() on it.'
        )

    def __init__(self, func, name=None):
        self.real_func = func
        self.__doc__ = getattr(func, '__doc__')

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
            self.func = self.real_func
        elif name != self.name:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                "(%r and %r)." % (self.name, name)
            )

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res
