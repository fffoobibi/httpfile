from typing import Any

from PyQt5.Qsci import QsciLexerXML

from . import register, TabCodeWidget


@register(file_types=['xml'])
class XMLCodeWidget(TabCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerXML(self)

