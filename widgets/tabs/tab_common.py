from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerTeX
# from PyQt5 import QsciLexerTeX

from . import register, TabCodeMixIn


@register(file_types=[''])
class TextCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self) -> Any:
        return QsciLexerTeX(self)

    def after_init(self):
        self._after_init()
