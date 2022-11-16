from PyQt5.Qsci import QsciLexerCSS

from . import register, TabCodeWidget


@register(file_types=['css'])
class CssCodeWidget(TabCodeWidget):
    file_type = 'css'

    def set_lexer(self):
        return QsciLexerCSS(self)
