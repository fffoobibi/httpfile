from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerHTML
from . import register, TabCodeMixIn


@register(file_types=['html'])
class HTMLCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self):
        return QsciLexerHTML(self)

    def after_init(self):
        self._after_init()
