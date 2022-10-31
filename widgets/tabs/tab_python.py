from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerPython

from widgets.base import PluginBaseMixIn

from . import register


@register(file_types=['py', 'pyw'])
class PythonCodeWidget(BaseCodeWidget, PluginBaseMixIn):
    def set_lexer(self) -> Any:
        return QsciLexerPython(self)

    def when_app_exit(self, main_app):
        print('python code close ===')
