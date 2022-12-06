# -*- coding: utf-8 -*-
# @Time    : 2022/11/29 17:02
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : __init__.py.py
# @Software: PyCharm
from pathlib import Path
from typing import List

from PyQt5.QtGui import QFontDatabase


class FontLoader(object):
    @classmethod
    def load(cls, fdb: QFontDatabase, path: str):
        pass


class SrcFontLoader(FontLoader):
    pass


class DirFontLoader(FontLoader):
    allow_types = ['ttf', 'wtf']

    @classmethod
    def load(cls, fdb: QFontDatabase, path: str) -> List[int]:
        p = Path(path)
        ret = []
        assert p.is_dir()
        for file in p.iterdir():
            if file.is_file() and file.name.split('.')[-1] in cls.allow_types:
                f_id = fdb.addApplicationFont(file.__str__())
                fontFamilies = fdb.applicationFontFamilies(f_id)
                print('familys: ', fontFamilies, file, fdb.isSmoothlyScalable(fontFamilies[0]), fdb.smoothSizes(fontFamilies[0], ''))

                ret.append(f_id)
        return ret
