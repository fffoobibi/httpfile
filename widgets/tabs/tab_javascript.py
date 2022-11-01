from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerJavaScript
from . import register, TabCodeMixIn


@register(file_types=['js'])
class JsCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self) -> Any:
        return QsciLexerJavaScript(self)

    def after_init(self):
        self._after_init()
