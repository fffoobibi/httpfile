from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerJava

from . import register, TabCodeMixIn


@register(file_types=['java'])
class JavaCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self) -> Any:
        return QsciLexerJava(self)

    def after_init(self):
        self._after_init()
