from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerJava

from . import register


@register(file_types=['java'])
class JavaCodeWidget(BaseCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerJava(self)
