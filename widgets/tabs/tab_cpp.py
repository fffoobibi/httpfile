from typing import Any

from PyQt5.Qsci import QsciLexerCPP

from . import register, TabCodeWidget


@register(file_types=['cpp'])
class CPPCodeWidget(TabCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerCPP(self)
