from typing import Any

from PyQt5.Qsci import QsciLexerBash

from . import register, TabCodeWidget


@register(file_types=['bash'])
class SQlCodeWidget(TabCodeWidget):
    file_type = 'bash'

    def set_lexer(self) -> Any:
        return QsciLexerBash(self)
