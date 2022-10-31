from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerCSS
from . import register


@register(file_types=['css'])
class CssCodeWidget(BaseCodeWidget):
    def set_lexer(self):
        return QsciLexerCSS(self)
