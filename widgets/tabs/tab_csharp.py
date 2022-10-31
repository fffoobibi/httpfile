from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerCSharp
from . import register, TabCodeMixIn


@register(file_types=['cs'])
class CSharpCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self):
        return QsciLexerCSharp(self)

    def after_init(self):
        self._after_init()
