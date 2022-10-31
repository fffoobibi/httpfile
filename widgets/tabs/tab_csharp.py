from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerCSharp
from . import register


@register(file_types=['cs'])
class CSharpCodeWidget(BaseCodeWidget):
    def set_lexer(self):
        return QsciLexerCSharp(self)
