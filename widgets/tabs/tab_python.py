from typing import Any

from PyQt5.Qsci import QsciLexerPython

from . import register, TabCodeWidget


@register(file_types=['py', 'pyw'])
class PythonCodeWidget(TabCodeWidget):
    def set_lexer(self) -> Any:
        return QsciLexerPython(self)

    def when_app_exit(self, main_app):
        pass
