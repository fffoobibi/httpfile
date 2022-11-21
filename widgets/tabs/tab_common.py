from typing import Any

from PyQt5.Qsci import QsciLexerTeX

from . import register, TabCodeWidget


# from PyQt5 import QsciLexerTeX


@register(file_types=['', 'log', 'ini', 'conf', 'cfg', 'txt'])
class TextCodeWidget(TabCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerTeX(self)
