from typing import Any

from PyQt5.Qsci import QsciLexerJavaScript

from . import register, TabCodeWidget


@register(file_types=['js'])
class JsCodeWidget(TabCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerJavaScript(self)

