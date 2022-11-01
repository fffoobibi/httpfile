from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerJSON

from . import register, TabCodeMixIn


@register(file_types=['json'])
class JsonCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self):
        return QsciLexerJSON(self)

    def after_init(self):
        self._after_init()
