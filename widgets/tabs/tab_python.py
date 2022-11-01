from typing import Any

from PyQt5.QtWidgets import QAction, QLineEdit

from pyqt5utils.components import Confirm
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
        self.search_action = QAction()
        self.search_action.setShortcut('ctrl+f')
        self.search_action.triggered.connect(self.search)
        self.addAction(self.search_action)

    def when_app_exit(self, main_app):
        print('python code close ===')

    def search(self):
        def ok():
            self.findFirstTarget(
                content.text(),

            )
        content = QLineEdit()
        Confirm.msg('搜索', target=self, content=content, ok=ok)
