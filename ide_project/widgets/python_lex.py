# -*- coding: utf-8 -*-
# @Time    : 2022/3/4 16:45
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : python_lex.py
# @Software: PyCharm


import autopep8
import yapf.yapflib.yapf_api as yapf

from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QCursor
from PyQt5.Qsci import QsciLexerPython

from .base_lex import BaseCodeWidget, Lexers


class CustomPythonLexer(QsciLexerPython):
    _key_words = ' '.join(dir(__builtins__)) + ' self super'

    def keywords(self, p_int):
        if p_int == 2:
            return self._key_words
        return super().keywords(p_int)

    def defaultColor(self, p_int):
        if p_int == self.Default:
            return Qt.white
        return super().defaultColor(p_int)

    def description(self, p_int):
        return 'ggg'


class PythonCodeWidget(BaseCodeWidget):
    type = Lexers.python
    custom_menu = True
    use_thread = True
    ast_thread = True

    actions = [('format_action', '格式化代码')]

    def set_font(self) -> QFont:
        try:
            ft = self.config.get_momo_font()
            return QFont(ft, 10)
        except:
            return QFont('微软雅黑', 10)

    def set_format(self, selected_text: str, all_text: str, *a) -> str:
        format_value = all_text
        format_type = a[0]
        if format_type == 'pep8':
            format_value = autopep8.fix_code(all_text, encoding='utf8')
        elif format_type == 'yapf':
            format_value, changed = yapf.FormatCode(all_text)
        return format_value

    def set_menu_policy(self, menu):
        f_menu = menu.addMenu('代码格式化')
        a1 = f_menu.addAction('pep8')
        a2 = f_menu.addAction('yapf')
        a3 = menu.addAction('语法树解析')
        act = menu.exec_(QCursor.pos())
        if act == a1:
            self.format_code('pep8')
        elif act == a2:
            self.format_code('yapf')
        elif act == a3:
            try:
                self._parse_ast()
            except:
                pass

    def set_lexer(self):
        python = CustomPythonLexer()
        python.setDefaultFont(QFont(self.set_font().family() or '微软雅黑', 10))
        d = QsciLexerPython.__dict__
        f = self.set_font()
        for k in d:
            if isinstance(d[k], int):
                python.setFont(f, d[k])

        python.setFoldQuotes(True)
        python.setFoldComments(True)
        python.setHighlightSubidentifiers(True)

        python.setColor(QColor('#53B323'), QsciLexerPython.FunctionMethodName)
        python.setColor(QColor('#A478F1'), QsciLexerPython.Operator)
        python.setColor(QColor('#0078D7'), QsciLexerPython.Number)
        python.setColor(QColor('#FFBA55'), QsciLexerPython.SingleQuotedString)
        python.setColor(QColor('#FFBA55'), QsciLexerPython.DoubleQuotedString)
        python.setColor(QColor('#FFBA55'), QsciLexerPython.TripleSingleQuotedString)
        python.setColor(QColor('#FFBA55'), QsciLexerPython.TripleDoubleQuotedString)
        python.setColor(QColor('#FFBA55'), QsciLexerPython.SingleQuotedFString)
        python.setColor(QColor('#FFBA55'), QsciLexerPython.DoubleQuotedFString)
        python.setColor(QColor('#FFBA55'), QsciLexerPython.TripleSingleQuotedFString)
        python.setColor(QColor('#FFBA55'), QsciLexerPython.TripleDoubleQuotedFString)

        python.setColor(QColor('#43B1FF'), QsciLexerPython.ClassName)
        python.setColor(QColor('#ACACAC'), QsciLexerPython.Comment)
        python.setColor(QColor('#ED005C'), QsciLexerPython.HighlightedIdentifier)
        python.setColor(Qt.white, QsciLexerPython.Default)
        python.setColor(Qt.white, QsciLexerPython.Identifier)
        python.setColor(QColor('#E5552F'), QsciLexerPython.Keyword)
        python.setColor(QColor('#FFBA55'), QsciLexerPython.UnclosedString)
        python.setColor(Qt.red, QsciLexerPython.CommentBlock)

        python.setFont(QFont(self.set_font().family() or '微软雅黑', 9), QsciLexerPython.Comment)
        return python

    def set_apis(self) -> List[str]:
        return []

    def set_run_cmd(self, file_name: str) -> str:
        if self.raw_file is None:
            return f'python {file_name}'
        else:
            return f'python {self.raw_file}'
