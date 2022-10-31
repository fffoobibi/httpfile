import threading
from typing import TypeVar, Generic, Any, Type
from pyqt5utils.decorators import singleton

__all__ = ('Provider',)


@singleton
class _Dict(object):
    _lock = threading.Lock()

    def __init__(self):
        self._values = {}

    def set(self, k, v):
        self._values[k] = v

    def get(self, k, dft=None):
        return self._values.get(k, dft)


_T = TypeVar('_T')


class Provider(Generic[_T]):
    _dict = _Dict()

    def __init__(self, t: Type[_T]):
        self._type: Type[_T] = t

    def set(self, t: _T) -> None:
        self._dict.set(self._type, t)

    def get(self, dft: Any = None) -> _T:
        return self._dict.get(self._type, dft)


if __name__ == '__main__':
    p1 = Provider(str)
    p1.set('this is a test')

    p2 = Provider(bool)
    p2.set(True)

    print(p1.get(), p2.get())
