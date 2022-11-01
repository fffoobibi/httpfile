from typing import Any

from PyQt5.Qsci import QsciLexerYAML

from . import register, TabCodeWidget


@register(file_types=['yaml'])
class YamlCodeWidget(TabCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerYAML(self)

