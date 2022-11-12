import time
from collections import deque
from types import MethodType
from typing import Any, List

import jedi
from PyQt5.Qsci import QsciLexerPython
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMenu
from cached_property import cached_property
from jedi.api.classes import Completion
from jedi.api.environment import SameEnvironment

from pyqt5utils.workers import WorkerManager
from widgets.factorys import make_styled
from . import register, TabCodeWidget


def hook_code_keyReleaseEvent(self, event):
    self.__class__.keyReleaseEvent(self, event)
    parent: PythonCodeWidget = self.code_container
    parent._input_logs.appendleft(time.time())
    print('add ', parent._input_logs)
    parent.auto_complete()
    # if parent._input_logs.__len__() == 2:
    #     a1, a2 = parent._input_logs[0], parent._input_logs[1]
    #     interval = a1 - a2
    #     if interval > 3:
    #         parent.auto_complete()
    # else:
    #     pass


@register(file_types=['py', 'pyw'])
class PythonCodeWidget(TabCodeWidget):

    def when_modify(self, position, modificationType, text, length, linesAdded,
                    line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded):
        super().when_modify(position, modificationType, text, length, linesAdded,
                            line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded)

        full = self.code.SC_MOD_INSERTTEXT | self.code.SC_MOD_DELETETEXT
        if ~modificationType & full == full:
            return
        self.code.wordAtLineIndex()

    # def after_init(self):
    #     self._input_logs = deque(maxlen=2)
    #     self.code.keyReleaseEvent = MethodType(hook_code_keyReleaseEvent, self.code)
    #     print('hook')

    @cached_property
    def jedi_worker(self):
        return WorkerManager().get(name='jedi_worker')

    def set_lexer(self) -> Any:
        return QsciLexerPython(self)

    def when_app_exit(self, main_app):
        pass

    def custom_menu_support(self):
        return True

    def auto_complete(self):
        position = self.code.currentPosition()
        line, col = self.code._current_line, self.code._current_col
        text = self.code.text(0, position)
        script = jedi.Script(text)
        # Completion
        ret: List[Completion] = script.complete(len(text.splitlines()), col)
        self.code._apis.clear()

        completions = [c.full_name for c in ret]
        print('set completions ', completions)
        for c in completions:
            self.code._apis.add(c)
        self.code._apis.prepare()
        self.code.autoCompleteFromAPIs()

    def custom_menu_policy(self, pos):

        menu: QMenu = make_styled(QMenu, 'menu')
        act = menu.addAction('运行')
        ac = menu.exec_(QCursor.pos())
        if ac == act:
            env: SameEnvironment = self.main_app.get_provider('python_info')
            if env:
                cmd = f'{env.executable} {self.file_path()}'
                print(cmd)

                # position = self.code.getGlobalCursorPosition()
                # global_position = self.code.mapToGlobal(position)
                # dy = self.code.textHeight(line)

                # self.code.autoCompleteFromDocument()
                # self.code.autoCompletionThreshold()

                # completer = QCompleter(['asdfsdf', 'dfdfdf'], self.code)
                # view = completer.popup()
                # view.show()
                # view.move(global_position + QPoint(0, dy))

                # com = ret[0]
                #
                # print(com.name)
                # print(com.name_with_symbols)
                # print(com.module_name)
                # print(com.full_name)
