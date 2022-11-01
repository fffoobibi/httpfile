from typing import Any

from PyQt5.Qsci import QsciLexerMarkdown

from . import register, TabCodeWidget


@register(file_types=['md'])
class MarkDownCodeWidget(TabCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerMarkdown(self)

