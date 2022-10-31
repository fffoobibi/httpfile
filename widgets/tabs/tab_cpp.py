from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerCPP

from . import register


@register(file_types=['cpp'])
class CPPCodeWidget(BaseCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerCPP(self)
