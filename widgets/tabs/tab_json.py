from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerJSON

from . import register


@register(file_types=['json'])
class JsonCodeWidget(BaseCodeWidget):
    def set_lexer(self):
        return QsciLexerJSON(self)
