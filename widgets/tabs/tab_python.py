import difflib
import keyword
import subprocess
import jedi

from typing import Any, List

from PyQt5.Qsci import QsciLexerPython
from PyQt5.QtCore import Qt, QDir, QTimer
from PyQt5.QtGui import QCursor, QKeySequence, QColor
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QTextEdit
from cached_property import cached_property
from jedi.api.classes import Completion
from jedi.api.environment import SameEnvironment

from pyqt5utils.workers import WorkerManager
from widgets.factorys import make_styled
from . import register, TabCodeWidget

from abc import ABC, abstractmethod


class FileTracerMixIn(object):
    def init_file_tracer(self):
        self.__hasChangeMarkers = False
        self.__oldText = self.monitor_text()
        self.__lastSavedText = self.monitor_text()
        self.__onlineChangeTraceTimer = QTimer(self)
        self.__onlineChangeTraceTimer.setSingleShot(True)
        self.__onlineChangeTraceTimer.setInterval(100)
        self.__onlineChangeTraceTimer.timeout.connect(
            self.__onlineChangeTraceTimerTimeout
        )
        monitor_widget = self.monitor_widget()
        monitor_widget.textChanged.connect(self.__resetOnlineChangeTraceTimer)

    def change_old_text(self, txt):
        self.__oldText = txt

    @abstractmethod
    def monitor_text(self) -> str:
        ...

    @abstractmethod
    def monitor_widget(self) -> QTextEdit:
        ...

    @abstractmethod
    def delete_all_changer_markers(self):
        ...

    @abstractmethod
    def add_change_markers(self, marker_infos: list):
        ...

    @abstractmethod
    def should_update_changed(self) -> bool:
        ...

    def tracer_file_name(self):
        return 'test.py'

    def __onlineChangeTraceTimerTimeout(self):
        if self.should_update_changed():
            self.delete_all_changer_markers()
            # step 1: mark saved changes
            oldL = self.__oldText.splitlines()
            newL = self.monitor_text().splitlines()

            file_name = self.tracer_file_name()

            lines = list(difflib.unified_diff(oldL, newL, fromfile=f'original', tofile=f'current'))
            if lines:
                import sys
                sys.stdout.writelines(lines)
                change_info = lines[2]
                change_contents = lines[3:]
                change_logs = []
                change_added = []
                change_subs = []
                starts = int(
                    change_info.replace('@', '').strip().split(' ')[0].split(',')[0].strip('-'))  # @@ -1,6 +1,7 @@
                print('\nstarts ', starts)
                print('change: ', change_contents)
                for index, content in enumerate(change_contents, starts - 1):
                    if '+' in content[:2]:
                        # if content.startswith('+'):
                        change_added.append([index, content])
                    elif '-' in content[:2]:
                        # elif  content.startswith('-'):
                        change_subs.append([index, content])
                print('change add', change_added)
                self.add_change_markers(change_added)
            # for line in lines[:3]
            # matcher = difflib.SequenceMatcher(None, oldL, newL)
            #
            # for token, _, _, j1, j2 in matcher.get_opcodes():
            #     if token in ["insert", "replace"]:
            #         for lineNo in range(j1, j2):
            #             self.markerAdd(lineNo, self.__changeMarkerSaved)
            #             self.__hasChangeMarkers = True
            #
            # # step 2: mark unsaved changes
            # oldL = self.__lastSavedText.splitlines()
            # newL = self.text().splitlines()
            # matcher = difflib.SequenceMatcher(None, oldL, newL)
            #
            # for token, _, _, j1, j2 in matcher.get_opcodes():
            #     if token in ["insert", "replace"]:
            #         for lineNo in range(j1, j2):
            #             self.markerAdd(lineNo, self.__changeMarkerUnsaved)
            #             self.__hasChangeMarkers = True
            #
            # if self.__hasChangeMarkers:
            #     self.changeMarkersUpdated.emit(self)
            #     self.__markerMap.update()

    def __resetOnlineChangeTraceTimer(self):
        self.__onlineChangeTraceTimer.stop()
        self.__onlineChangeTraceTimer.start()


@register(file_types=['py', 'pyw'])
class PythonCodeWidget(TabCodeWidget, FileTracerMixIn):
    def should_update_changed(self) -> bool:
        return self._file_loaded

    def monitor_text(self) -> str:
        return self.code.text()

    def monitor_widget(self) -> QTextEdit:
        return self.code

    def delete_all_changer_markers(self):
        self.code.markerDeleteAll(self.save_changed_marker_number)

    def add_change_markers(self, marker_infos: list):
        for line, content in marker_infos:
            self.code.markerAdd(line, self.save_changed_marker_number)

    save_changed_margin_line_type = 1
    save_changed_marker_number = 0
    save_changed_marker_handler: int  # type hint

    def when_modify(self, position, modificationType, text, length, linesAdded,
                    line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded):
        super().when_modify(position, modificationType, text, length, linesAdded,
                            line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded)

        full = self.code.SC_MOD_INSERTTEXT | self.code.SC_MOD_DELETETEXT
        if ~modificationType & full == full:
            return

    def after_init(self):
        self.set_commands()
        self.define_margins()
        self.init_file_tracer()

    def __format_code(self):
        pass

    def __upper_or_lower_word(self):
        line, col = self.code.current_line_col
        text = self.code.wordAtLineIndex(line, col)

        self.code.moveCursorWordLeft()
        line, col = self.code.current_line_col
        text_left = self.code.wordAtLineIndex(line, col)
        if text_left != text:
            self.code.moveCursorWordRight()
            line, col = self.code.current_line_col
            text = self.code.wordAtLineIndex(line, col)

        pos = self.code.currentPosition()
        if text.islower():
            fmt_text = text.upper()
        else:
            fmt_text = text.lower()
        self.code.replaceRange(pos, len(text), fmt_text)

    def set_commands(self):
        def complete():
            self.auto_complete()

        editor = self.code
        commands = editor.standardCommands()
        commands_list = [(Qt.ControlModifier | Qt.Key_Tab, complete),
                         (Qt.ControlModifier | Qt.Key_P, self.__upper_or_lower_word)]
        for key, func in commands_list:
            command = commands.boundTo(key)
            # clear the default
            if command is not None:
                command.setKey(0)
            # set command
            action = QAction(f'{func.__name__}', self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(func)
            editor.addAction(action)

    def load_file(self, file_path, content: str = None):
        super(PythonCodeWidget, self).load_file(file_path, content)
        self.change_old_text(self.monitor_text())

    def define_margins(self):
        editor = self.code

        try:
            from PyQt5 import QsciScintilla
        except:
            from PyQt5.Qsci import QsciScintilla

        editor.markerDefine(editor.MarkerSymbol.FullRectangle, self.save_changed_marker_number)
        editor.setMarkerBackgroundColor(QColor('darkgreen'), self.save_changed_marker_number)

        editor: QsciScintilla
        editor.setMarginLineNumbers(0, True)
        editor.setMarginSensitivity(0, True)
        editor.setMarginWidth(0, '00')

        editor.setMarginType(self.save_changed_margin_line_type, editor.MarginType.SymbolMargin)
        editor.setMarginWidth(self.save_changed_margin_line_type, '0')

    @cached_property
    def jedi_worker(self):
        return WorkerManager().get(name='jedi_worker')

    def set_apis(self) -> List[str]:
        return keyword.kwlist + dir(__builtins__)

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
        completions = [c.full_name for c in ret]
        for c in completions:
            self.code._apis.add(c)
        self.code._apis.prepare()
        self.code.autoCompleteFromAPIs()
        print('raws -:', self.code._apis.installedAPIFiles())

    def custom_menu_policy(self, pos):

        menu: QMenu = make_styled(QMenu, 'menu')
        if not self.is_remote:
            ac0 = menu.addAction('打开于文件夹')
            menu.addSeparator()

        act = menu.addAction('运行')
        ac1 = menu.addAction('格式化', self.__format_code, shortcut=QKeySequence('ctrl+shift+l'))
        ac2 = menu.addAction('大小写', self.__upper_or_lower_word, shortcut=QKeySequence('ctrl+p'))
        ac3 = menu.addAction('文件比较')
        ac = menu.exec_(QCursor.pos())
        if not self.is_remote:
            if ac == ac0:
                path = QDir.toNativeSeparators(self.file_path())
                subprocess.Popen(f'explorer /select, {path}', shell=True)
                return

        if ac == act:
            env: SameEnvironment = self.main_app.get_provider('python_info')
            if env:
                cmd = f'{env.executable} {self.file_path()}'
                print(cmd)
                self.auto_complete()
        elif ac == ac3:
            self._new = self.code.text().splitlines(True)
            lines = list(difflib.unified_diff(self._old, self._new, fromfile='a.py', tofile='b.py'))
            import sys
            sys.stdout.writelines(lines)
            # print(len(self._old), len(lines))
            print(lines)
