from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerYAML

from . import register, TabCodeMixIn


@register(file_types=['yaml'])
class YamlCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self) -> Any:
        return QsciLexerYAML(self)

    def after_init(self):
        self._after_init()
