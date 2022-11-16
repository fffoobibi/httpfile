from typing import Any

from PyQt5.Qsci import QsciLexerJava

from . import register, TabCodeWidget


@register(file_types=['java'])
class JavaCodeWidget(TabCodeWidget):
    file_type = 'java'

    def set_lexer(self) -> Any:
        return QsciLexerJava(self)
