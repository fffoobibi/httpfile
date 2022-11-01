from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerXML

from . import register, TabCodeMixIn


@register(file_types=['xml'])
class XMLCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self) -> Any:
        return QsciLexerXML(self)

    def after_init(self):
        self._after_init()
