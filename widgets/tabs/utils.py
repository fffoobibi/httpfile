# -*- coding: utf-8 -*-
# @Time    : 2022/12/1 15:48
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : utils.py
# @Software: PyCharm
from contextlib import contextmanager

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


if __name__ == '__main__':
    # dic = {'uri': 'file:///c:/Users/fqk12/Desktop/httpfile/scrap.py', 'start': {'line': 17, 'character': 48},
    #        'end': {'line': 17, 'character': 55}}
    s = ObjDict(uri='file:///c:/Users/fqk12/Desktop/httpfile/scrap.py',
                start=ObjDict(**{'line': 17, 'character': 48}),
                end=ObjDict(**{'line': 17, 'character': 55}))
    print(s.start.line)
