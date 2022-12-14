# -*- coding: utf-8 -*-
# @Time    : 2022/12/1 15:48
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : utils.py
# @Software: PyCharm
import types
import typing
from contextlib import contextmanager
from typing import Type, Callable

from PyQt5.QtWidgets import QFrame, QHBoxLayout
from jedi import RefactoringError


@contextmanager
def hook_jedi_context():
    def _apply(self):
        if self._from_path is None:
            raise RefactoringError(
                'Cannot apply a refactoring on a Script with path=None'
            )

        with open(self._from_path, 'w', newline='', encoding='utf-8') as f:
            f.write(self.get_new_code())

    try:
        from jedi.api.refactoring import ChangedFile
        old = ChangedFile.apply
        ChangedFile.apply = _apply
        yield
    finally:
        ChangedFile.apply = old


def make_h_panel(spacing=0, margins=0):
    frame = QFrame()
    frame.setFrameShape(QFrame.NoFrame)
    lay = QHBoxLayout(frame)
    lay.setSpacing(spacing)
    lay.setContentsMargins(margins, margins, margins, margins)
    return lay, frame


class ObjDict(dict):
    def __getattr__(self, item):
        return self[item]


def dict_to_obj(dic):
    return ObjDict(**dic)


def must_call_super(parent: Type):
    def wrapper(func):
        def inner(self, *a, **kw):
            super_func = getattr(parent, func.__name__, None)
            if super_func and super_func != func:
                super_func(self, *a, **kw)
            ret = func(self, *a, **kw)
            return ret

        return inner

    return wrapper


def get_function(f: Callable[..., typing.Any]) -> types.FunctionType:
    if isinstance(f, types.MethodType):
        return f.__func__
    f: types.FunctionType
    return f


if __name__ == '__main__':
    # dic = {'uri': 'file:///c:/Users/fqk12/Desktop/httpfile/scrap.py', 'start': {'line': 17, 'character': 48},
    #        'end': {'line': 17, 'character': 55}}
    s = ObjDict(uri='file:///c:/Users/fqk12/Desktop/httpfile/scrap.py',
                start=ObjDict(**{'line': 17, 'character': 48}),
                end=ObjDict(**{'line': 17, 'character': 55}))
    print(s.start.line)
