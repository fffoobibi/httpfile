from PyQt5.Qsci import QsciLexerCSharp

from . import register, TabCodeWidget


@register(file_types=['cs'])
class CSharpCodeWidget(TabCodeWidget):
    def set_lexer(self):
        return QsciLexerCSharp(self)
