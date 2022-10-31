# -*- coding: utf-8 -*-
# @Time    : 2022/3/4 16:50
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : LexConfig.py
# @Software: PyCharm
from enum import IntEnum

from PyQt5.QtWidgets import QWidget

from .json_lex import JsonCodeWidget
from .python_lex import PythonCodeWidget
from .base_lex import Themes, Lexers
from .text_lex import TextCodeWidget


class LexGetter(object):
    theme: Themes = Themes.dark

    def __init__(self):
        pass

    @classmethod
    def get_lexer(cls, theme: Themes, file_name: str, type: Lexers, output: QWidget, raw_file: str, config=None):
        if type == Lexers.python:
            return PythonCodeWidget(file_name, theme, output, raw_file, config)
        elif type == Lexers.text:
            return TextCodeWidget(file_name, theme, output, raw_file, config)
        elif type == Lexers.json:
            return JsonCodeWidget(file_name, theme, output, raw_file, config)
