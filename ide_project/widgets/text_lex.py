# -*- coding: utf-8 -*-
# @Time    : 2022/3/4 16:45
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : python_lex.py
# @Software: PyCharm

from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.Qsci import QsciLexerPython

from .base_lex import BaseCodeWidget, Themes, Lexers


class TextCodeWidget(BaseCodeWidget):
    type = Lexers.text

    def set_lexer(self):
        self.setColor(Qt.lightGray)
        self.setFont(QFont('等线', 9))
        self.update()
        return None

    def set_run_cmd(self, file_name: str) -> str:
        return
