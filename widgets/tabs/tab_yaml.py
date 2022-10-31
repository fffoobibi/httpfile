from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerYAML

from . import register


@register(file_types=['yaml'])
class YamlCodeWidget(BaseCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerYAML(self)
