from typing import Any

from PyQt5.Qsci import QsciLexerYAML

from . import register, TabCodeWidget


@register(file_types=['yaml', 'yml'])
class YamlCodeWidget(TabCodeWidget):
    file_type = 'yaml'

    def set_lexer(self) -> Any:
        return QsciLexerYAML(self)
