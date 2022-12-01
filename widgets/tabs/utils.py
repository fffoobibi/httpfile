# -*- coding: utf-8 -*-
# @Time    : 2022/12/1 15:48
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : utils.py
# @Software: PyCharm
from contextlib import contextmanager

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
