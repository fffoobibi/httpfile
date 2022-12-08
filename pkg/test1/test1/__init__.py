# -*- coding: utf-8 -*-
# @Time    : 2022/12/7 16:26
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : __init__.py.py
# @Software: PyCharm

from importlib_metadata import entry_points

display_eps = entry_points(group='test1.hello')
try:
    print('dsp -----')
    hello = display_eps[0].load()
except IndexError:
    def hello():
        print('fuck you hello1')


def hifu():
    hello()
