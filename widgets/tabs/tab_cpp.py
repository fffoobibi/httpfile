from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerCPP

from . import register, TabCodeMixIn


@register(file_types=['cpp'])
class CPPCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self) -> Any:
        return QsciLexerCPP(self)

    def after_init(self):
        self._after_init()
