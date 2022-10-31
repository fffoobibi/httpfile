from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerMarkdown
from . import register


@register(file_types=['md'])
class MarkDownCodeWidget(BaseCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerMarkdown(self)
