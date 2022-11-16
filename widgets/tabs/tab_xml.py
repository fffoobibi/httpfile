from typing import Any

from PyQt5.Qsci import QsciLexerXML

from . import register, TabCodeWidget


@register(file_types=['xml'])
class XMLCodeWidget(TabCodeWidget):
    file_type = 'xml'

    def set_lexer(self) -> Any:
        return QsciLexerXML(self)
