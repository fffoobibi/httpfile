from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerMarkdown
from . import register, TabCodeMixIn


@register(file_types=['md'])
class MarkDownCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self) -> Any:
        return QsciLexerMarkdown(self)

    def after_init(self):
        self._after_init()
