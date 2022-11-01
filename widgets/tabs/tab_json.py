from PyQt5.Qsci import QsciLexerJSON

from . import register, TabCodeWidget


@register(file_types=['json'])
class JsonCodeWidget(TabCodeWidget):
    def set_lexer(self):
        return QsciLexerJSON(self)

