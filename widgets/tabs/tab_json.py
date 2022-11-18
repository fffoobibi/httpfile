from PyQt5.Qsci import QsciLexerJSON

from . import register, TabCodeWidget


@register(file_types=['json', 'ipynb'])
class JsonCodeWidget(TabCodeWidget):
    file_type = 'json'

    def set_lexer(self):
        return QsciLexerJSON(self)
