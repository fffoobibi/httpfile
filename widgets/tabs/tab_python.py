from typing import Any

from pyqt5utils.qsci.base import BaseCodeWidget
from PyQt5.Qsci import QsciLexerPython

from widgets.base import PluginBaseMixIn

from . import register, TabCodeMixIn


@register(file_types=['py', 'pyw'])
class PythonCodeWidget(BaseCodeWidget, TabCodeMixIn):
    def set_lexer(self) -> Any:
        return QsciLexerPython(self)

    def after_init(self):
        self._after_init()

    def when_app_exit(self, main_app):
        print('python code close ===')
