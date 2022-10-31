from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerHTML
from . import register


@register(file_types=['html'])
class HTMLCodeWidget(BaseCodeWidget):
    def set_lexer(self):
        return QsciLexerHTML(self)
