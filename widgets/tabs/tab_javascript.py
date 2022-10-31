from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerJavaScript
from . import register


@register(file_types=['js'])
class JsCodeWidget(BaseCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerJavaScript(self)
