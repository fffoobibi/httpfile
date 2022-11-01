from typing import Any

from PyQt5.Qsci import QsciLexerPython
from PyQt5.QtWidgets import QLineEdit

from pyqt5utils.components import Confirm
from . import register, TabCodeWidget


@register(file_types=['py', 'pyw'])
class PythonCodeWidget(TabCodeWidget):
    def set_lexer(self) -> Any:
        print('python ', self)
        return QsciLexerPython(self)

    def when_app_exit(self, main_app):
        print('python code close ===', self.file_path())

    def search(self):
        # from PyQt5 import QsciScintilla
        def ok():
            ret = self.findFirstTarget(
                content.text(), False, False, False, -1, -1, -1, -1
            )
            if ret:
                target = self.getFoundTarget()
                print('found ', target)
                start_line, start_index = self.lineIndexFromPosition(target[0])
                end_line, end_index = self.lineIndexFromPosition(target[0] + target[1])
                self.setRectangularSelection(start_line, start_index, end_line, end_index)

            # print('find ', ret, content.text())
            # QsciScintilla.findFirst()
            # self.findNextTarget()
            # self.flashFindIndicator(0, 0, self.lines() - 1, 0)
            # self.showFindIndicator(0, 0, self.lines()-1, 0)
            # self.showFindIndicator()

        content = QLineEdit()
        Confirm.msg('搜索', target=self, content=content, ok=ok)
