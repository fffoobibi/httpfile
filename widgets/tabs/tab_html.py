from PyQt5.Qsci import QsciLexerHTML

from . import register, TabCodeWidget


@register(file_types=['html'])
class HTMLCodeWidget(TabCodeWidget):
    file_type = 'html'

    def set_lexer(self):
        return QsciLexerHTML(self)
