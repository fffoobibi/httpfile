from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerCSS
from . import register, TabCodeMixIn


@register(file_types=['css'])
class CssCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self):
        return QsciLexerCSS(self)

    def after_init(self):
        self._after_init()
