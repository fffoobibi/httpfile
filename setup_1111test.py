# -*- coding: utf-8 -*-
# @Time    : 2022/12/7 15:57
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : setup_test.py
# @Software: PyCharm


from importlib_metadata import entry_points
esp = entry_points(group='json_lsp.main:load')
print(esp)


import json_lsp