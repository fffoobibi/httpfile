import difflib
import keyword
import subprocess
import sys
from abc import abstractmethod
from pathlib import Path
from types import MethodType
from typing import Any, List

import jedi
from PyQt5.Qsci import QsciLexerPython, QsciScintilla
from PyQt5.QtCore import Qt, QDir, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QCursor, QKeySequence, QColor, QIcon, QFont
from PyQt5.QtWidgets import QMenu, QAction, QTextEdit, QTextBrowser, QLineEdit, QPushButton, QLabel, QListWidget
from cached_property import cached_property
from jedi.api import errors
from jedi.api.classes import Completion, Name
from jedi.api.environment import SameEnvironment
from lsprotocol.types import ClientCapabilities

from lsp.interface import StdIoLanguageClient, TCPLanguageClient
from lsp.utils import LspContext
from pyqt5utils.components.helper import ObjectsHelper
from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.components.widgets.dialogs import ShadowDialog
from pyqt5utils.qsci.scintillacompat import QsciScintillaCompat
from pyqt5utils.workers import WorkerManager
from widgets.factorys import make_styled, add_styled
from . import register, TabCodeWidget
from .helpers import get_ref_line_words
from .utils import make_h_panel
from ..signals import signal_manager
from ..styles import current_styles


class FileTracerMixIn(object):

    def init_file_tracer(self):
        self.__hasChangeMarkers = False
        self.__old_text = self.monitor_text()
        self.__last_saved_text = self.monitor_text()
        self.__onlineChangeTraceTimer = QTimer()
        self.__onlineChangeTraceTimer.setSingleShot(True)
        self.__onlineChangeTraceTimer.setInterval(300)
        self.__onlineChangeTraceTimer.timeout.connect(self.__online_change_trace_timer_timeout)
        monitor_widget = self.monitor_widget()
        monitor_widget.textChanged.connect(self.__reset_online_change_trace_timer)
        self.define_file_trace_margins()

    def change_old_text(self, txt):
        self.__old_text = txt

    def reset_file_tracer(self):
        self.__old_text = self.monitor_text()
        self.delete_all_changer_markers()

    @abstractmethod
    def define_file_trace_margins(self):
        ...

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
    def add_change_markers(self, marker_infos: list, maker_subs: list):
        ...

    @abstractmethod
    def should_update_changed(self) -> bool:
        ...

    def __online_change_trace_timer_timeout(self):
        if self.should_update_changed():
            self.delete_all_changer_markers()
            old_lines = self.__old_text.splitlines(True)
            new_lines = self.monitor_text().splitlines(True)
            lines = list(difflib.unified_diff(old_lines, new_lines, fromfile=f'original', tofile=f'current', ))
            if lines:
                # sys.stdout.writelines(lines)
                change_info = lines[2]
                change_contents = lines[3:]
                change_added = []
                change_subs = []
                line_start = int(
                    change_info.replace('@', '').strip().split(' ')[0].split(',')[0].strip('-'))  # @@ -1,6 +1,7 @@
                # print('\nstarts ', line_start)
                add_line = line_start - 1
                subs_line = line_start - 1
                i = line_start - 1
                for index, content in enumerate(change_contents, line_start - 1):
                    i += 1
                    if content.startswith('+'):  # file new
                        add_line += 1
                        change_added.append([add_line, content])
                    elif content.startswith('-'):  # file old
                        subs_line += 1
                        change_subs.append([subs_line, content])
                    elif content[0] == ' ':  # and index != 0:  # no change
                        add_line += 1
                        subs_line += 1
                # print('added: ', change_added)
                # print('delete: ', change_subs)
                self.add_change_markers(change_added, change_subs)

    def __reset_online_change_trace_timer(self):
        self.__onlineChangeTraceTimer.stop()
        self.__onlineChangeTraceTimer.start()


class StyledPythonLexer(QsciLexerPython):
    def __init__(self, parent):
        super(StyledPythonLexer, self).__init__(parent)
        self.setHighlightSubidentifiers(True)

    def keywords(self, set: int) -> str:
        st = super().keywords(set)
        return f'{st} self'

    def defaultPaper(self, style: int) -> QColor:
        try:
            return QColor(current_styles.editor_python['paper']['background'])
        except:
            return super().defaultPaper(style)

    def defaultColor(self, style):
        color = current_styles.get_editor_color(current_styles.editor_python.get('color'), style)
        if color:
            return QColor(color)
        return super(StyledPythonLexer, self).defaultColor(style)

    def defaultFont(self, p_int):
        font: QFont = super().defaultFont(p_int)
        font_family = current_styles.editor_python.get('font', {}).get('default', None)
        if font_family is not None:
            font.setFamily(font_family)
            font.setPointSizeF(10)
            font.setBold(False)
        return font


@register(file_types=['py', 'pyw'])
class PythonCodeWidget(TabCodeWidget, FileTracerMixIn):
    file_type = 'python'

    tracer_margin_type = 1

    add_marker_number = 0
    deleted_marker_number = 1
    modify_marker_number = 2

    # indicators
    jedi_ref_indicator = 10
    jedi_syntax_indicator = 11

    # save_changed_marker_handler: int  # type hint
    after_saved = pyqtSignal()
    file_loaded = pyqtSignal()

    def define_file_trace_margins(self):
        editor: QsciScintilla
        editor = self.code
        editor.markerDefine(editor.MarkerSymbol.FullRectangle, self.add_marker_number)  # add
        editor.setMarkerBackgroundColor(QColor('darkgreen'), self.add_marker_number)
        editor.setMarkerForegroundColor(QColor('red'), self.add_marker_number)
        editor.markerDefine(editor.MarkerSymbol.ThreeDots, self.deleted_marker_number)  # deleted
        editor.setMarkerForegroundColor(QColor('red'), self.deleted_marker_number)
        editor.markerDefine(editor.MarkerSymbol.FullRectangle, self.modify_marker_number)  # modify
        editor.setMarkerBackgroundColor(QColor('#F38922'), self.modify_marker_number)  # 橘色

        editor.setMarginLineNumbers(0, True)
        editor.setMarginSensitivity(0, True)
        editor.setMarginWidth(0, '00')

        editor.setMarginType(self.tracer_margin_type, editor.MarginType.SymbolMargin)

        editor.setMarginWidth(self.tracer_margin_type, '0')

    def should_update_changed(self) -> bool:

        return self._file_loaded

    def monitor_text(self) -> str:

        return self.code.text()

    def monitor_widget(self) -> QTextEdit:

        return self.code

    def delete_all_changer_markers(self):

        self.code.markerDeleteAll(self.add_marker_number)

    def add_change_markers(self, marker_infos: list, marker_subs: list):
        # modify
        s1 = set([line for line, content in marker_infos])
        s2 = set([line for line, content in marker_subs])
        modified = s1 & s2
        for line in modified:
            self.code.markerAdd(line - 1, self.modify_marker_number)

        # newlines
        new_line = s1 - s2
        for line in new_line:
            self.code.markerAdd(line - 1, self.add_marker_number)  # new line

        # for line, content in marker_infos:
        #     self.code.markerAdd(line - 1, self.save_changed_marker_number)  # new line

    def when_modify(self, position, modificationType, text, length, linesAdded,
                    line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded):
        super().when_modify(position, modificationType, text, length, linesAdded,
                            line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded)

        full = self.code.SC_MOD_INSERTTEXT | self.code.SC_MOD_DELETETEXT
        if ~modificationType & full == full:
            return

    def after_init(self):
        self.set_commands()
        self.init_file_tracer()
        self.code._has_alt_control = False
        self.code.support_language_parse = True
        self.code.setMouseTracking(True)
        self.after_saved.connect(self.reset_file_tracer)
        self.define_jedi_indicators()
        self.file_loaded.connect(self.when_file_loaded)

    def when_file_loaded(self):
        self.code.onTextDocumentDidOpen(self.file_path(),
                                        'python', 0, self.code.text()
                                        )

    def when_remove(self):
        if getattr(self.code, '_debounce_timer', None):
            self.code._debounce_timer.stop()
        self.code.onTextDocumentDidClose(self.file_path())

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

    @cached_property
    def jedi_worker(self):
        return WorkerManager().get(name='jedi_worker')

    def set_apis(self) -> List[str]:
        return keyword.kwlist + dir(__builtins__)

    def set_lexer(self) -> Any:
        return StyledPythonLexer(self)

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

    def custom_menu_policy(self, pos):

        menu: QMenu = make_styled(QMenu, 'menu')
        if not self.is_remote:
            ac0 = menu.addAction('打开于文件夹')
            menu.addSeparator()

        act = menu.addAction(QIcon(':/icon/运行，调试.svg'), '运行')
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
            signal_manager.emit(signal_manager.runPython, self.file_path())
        elif ac == ac3:
            print(repr(self.monitor_text()))

    @property
    def has_control_focus(self):
        return self._has_control

    def define_jedi_indicators(self):
        editor = self.code

        editor: QsciScintillaCompat

        editor.indicatorDefine(editor.StraightBoxIndicator, self.code.indic_brace)
        editor.setIndicatorDrawUnder(True, self.code.indic_brace)
        editor.setIndicatorForegroundColor(QColor('red'), self.code.indic_brace)
        editor.setMatchedBraceIndicator(self.code.indic_brace)
        editor.setIndicatorAlpha(self.code.indic_brace, 200)
        editor.setIndicatorOutAlpha(self.code.indic_brace, 0)

        editor.indicatorDefine(editor.StraightBoxIndicator, self.code.indic_ref)
        editor.setIndicatorDrawUnder(True, self.code.indic_ref)
        editor.setIndicatorForegroundColor(QColor(current_styles.editor_python['statics'].get('indic_ref')
                                                  ), self.code.indic_ref)

        editor.indicatorDefine(editor.StraightBoxIndicator, self.code.indic_ref_class)
        editor.setIndicatorDrawUnder(True, self.code.indic_ref_class)
        editor.setIndicatorForegroundColor(QColor(current_styles.editor_python['statics'].get('indic_ref_class')
                                                  ), self.code.indic_ref_class)

        editor.indicatorDefine(editor.StraightBoxIndicator, self.code.indic_ref_define)
        editor.setIndicatorDrawUnder(True, self.code.indic_ref_define)
        editor.setIndicatorForegroundColor(QColor(current_styles.editor_python['statics'].get('indic_ref_define')
                                                  ), self.code.indic_ref_define)

        editor.indicatorDefine(editor.SquigglePixmapIndicator, self.code.indic_diagnostics)
        editor.setIndicatorDrawUnder(True, self.code.indic_diagnostics)
        editor.setIndicatorForegroundColor(QColor('red'), self.code.indic_diagnostics)

        # editor.setIndicatorOutlineColor(Qt.green, self.code.indic_ref)

    def create_dynamic_actions(self):
        def render_custom_style(this):
            foreground = current_styles.foreground
            this.setStyleSheet(
                'QPushButton{color:%s;font-family:微软雅黑;background:transparent;border:none;padding:3px 4px;}'
                'QPushButton::menu-indicator {image: none; width:0px}'
                'QPushButton:hover{background:%s}' % (foreground, current_styles.toolbar_hover))

            next_btn.setStyleSheet('QPushButton{color:%s;font-family:微软雅黑;background:transparent;border:none}'
                                   'QPushButton:hover{background:%s}' % (foreground, current_styles.toolbar_hover))
            pre_btn.setStyleSheet('QPushButton{color:%s;font-family:微软雅黑;background:transparent;border:none}'
                                  'QPushButton:hover{background:%s}' % (foreground, current_styles.toolbar_hover))
            label.setStyleSheet(
                'QPushButton{color:%s;font-family:微软雅黑;background:transparent;border:none;padding:3px 4px;}'
                'QPushButton:hover{background:%s}' % (foreground, current_styles.toolbar_hover))

        def _next_action():
            if self.code.current_refs:
                ref = self.code.current_refs.next()
                self.move_to(ref.range.start.line, ref.range.start.character, True)

        def _previous_action():
            if self.code.current_refs:
                ref = self.code.current_refs.previous()
                self.move_to(ref.range.start.line, ref.range.start.character, True)

        def _show_refs():
            style_sheet = '#FrameLess{background:%s;border:1px solid %s}' % (current_styles.background_darker,
                                                                             current_styles.border)
            sh = ShadowDialog(frame_less_style=style_sheet, shadow_color='transparent')
            listview = QListWidget()
            for ref, file_name in get_ref_line_words(self.code.current_refs, self.code):
                line = self.code.text(ref.range.start.line).strip()
                listview.addItem(f'{file_name}({ref.range.start.line}:{ref.range.start.character}): {line}')

            listview.setStyleSheet(
                'QListWidget{border:none;background:%s;color:%s}' % (
                    current_styles.background_lighter, current_styles.foreground))
            StylesHelper.set_h_history_style_dynamic(listview, color=current_styles.handler, background='transparent',
                                                     height=10)
            StylesHelper.set_v_history_style_dynamic(listview, color=current_styles.handler, background='transparent',
                                                     width=10)
            title = QLabel()
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet('QLabel{font-family:微软雅黑;padding:4px;color:%s}' % current_styles.foreground)
            title.setText('引用关系')
            sh.setFixedWidth(ObjectsHelper.window_size()[0] / 2.5)
            sh.add_content(title)
            sh.add_content(listview)
            sh.center(self.main_app)

        lay, frame = make_h_panel()
        btn = QPushButton()
        btn.setIcon(QIcon(':/icon/fenxi.svg'))
        btn.setText(' 静态分析')
        btn.setToolTip('静态分析')
        btn.render_custom_style = MethodType(render_custom_style, btn)
        lay.addWidget(btn)

        menu: QMenu = make_styled(QMenu, 'menu')
        a0 = menu.addAction('全选')
        a1 = menu.addAction('错误检查')
        a2 = menu.addAction('引用分析')
        a3 = menu.addAction('代码跳转')
        a4 = menu.addAction('悬浮提示')
        a0.setCheckable(True)
        a1.setCheckable(True)
        a2.setCheckable(True)
        a3.setCheckable(True)
        a4.setCheckable(True)
        btn.setMenu(menu)
        label = QPushButton()
        label.clicked.connect(_show_refs)
        next_btn = QPushButton()
        pre_btn = QPushButton()
        pre_btn.setIcon(QIcon(':/icon/jiantou_liebiaoshouqi.svg'))
        next_btn.setIcon(QIcon(':/icon/jiantou_liebiaozhankai.svg'))

        if len(self.code.current_refs) == 0:
            next_btn.hide()
            pre_btn.hide()
        else:
            next_btn.show()
            pre_btn.show()

        lay.addWidget(label)
        lay.addWidget(next_btn)
        lay.addWidget(pre_btn)

        next_btn.clicked.connect(_next_action)
        pre_btn.clicked.connect(_previous_action)
        add_styled(btn, 'custom-style')
        self.store_data_clear('action')
        self.store_data((label, next_btn, pre_btn), 'action', )

        return frame

    # language server

    def _render_tip(self, msg: str, when_close=None, line_str=None):
        background = current_styles.background_lighter
        border = current_styles.border_lighter
        foreground = current_styles.foreground
        tip_shadow = ShadowDialog(
            shadow_color='transparent',
            frame_less_style='#FrameLess{background:%s;color:%s;font-family:微软雅黑;border:1px solid %s}' % (
                background, foreground, border
            ))

        tip_shadow.when_close = when_close
        text = QTextBrowser()
        text.setHtml(msg)
        text.setStyleSheet('QTextBrowser{background:%s;color:%s;font-family:微软雅黑;border:none}' % (
            background, foreground
        ))

        if line_str:
            fw = text.fontMetrics().width(line_str) + 10 * 2 + 8 + 20
            tip_shadow.setMinimumWidth(fw)

        StylesHelper.set_h_history_style_dynamic(text, color=current_styles.handler, height=8, background='transparent')
        StylesHelper.set_v_history_style_dynamic(text, color=current_styles.handler, width=8, background='transparent')
        tip_shadow.add_content(text)
        point = self.code.mapFromGlobal(QCursor.pos())
        tip_shadow.pop_with_position(self, dx=point.x(), dy=point.y())

    def _render_rename(self, word: str, confirm, when_close=None, line_str=None):
        def wrapper_confirm():
            renamed = text.text().strip()
            if renamed:
                tip_shadow.close()
                confirm(renamed)

        background = current_styles.background_lighter
        border = current_styles.border_lighter
        foreground = current_styles.foreground
        tip_shadow = ShadowDialog(
            shadow_color='transparent',
            frame_less_style='#FrameLess{background:%s;color:%s;font-family:微软雅黑;border:1px solid %s}' % (
                background, foreground, border
            ))

        tip_shadow.when_close = when_close
        text = QLineEdit()
        text.setPlaceholderText(word)
        text.setStyleSheet('QLineEdit{background:%s;color:%s;font-family:微软雅黑;border:none}' % (
            background, foreground
        ))
        text.setClearButtonEnabled(True)
        text.returnPressed.connect(wrapper_confirm)
        if line_str:
            fw = text.fontMetrics().width(line_str) + 10 * 2 + 8 + 20
            tip_shadow.setMinimumWidth(fw)
        tip_shadow.add_content(text)
        left_0 = self.code.mapToGlobal(QPoint(0, 0))
        point = self.code.getGlobalCursorPosition()
        point = self.code.mapToGlobal(point)
        point = point - left_0
        point.setY(point.y() + self.code.textHeight(self.code.current_line_col[0]))
        tip_shadow.pop_with_position(self, dx=point.x(), dy=point.y())
        text.setFocus(True)

    language_client_class = StdIoLanguageClient  # , TCPLanguageClient

    def capacities(self) -> int:
        editor = self.code
        return editor.ref_flag | editor.rename_flag | editor.infer_flag | editor.completion_flag  # | editor.hover_flag

    def lsp_init_kw(self) -> dict:
        if self.language_client_class is StdIoLanguageClient:
            proc = subprocess.Popen([
                'pylsp',
                # '--tcp',
                # 'jedi-language-server',
                # '-v'
            ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            return dict(reader=proc.stdout, writer=proc.stdin)
        else:  # tcp
            return dict(host='127.0.0.1', port=2087)

    def lsp_serve_name(self) -> str:
        return 'pylsp'

    def clientCapacities(self) -> ClientCapabilities:
        with LspContext() as c:
            t = c.type
            r = t.ClientCapabilities(
                window=t.WindowClientCapabilities(
                    work_done_progress=True,
                    show_message=t.ShowMessageRequestClientCapabilities(),
                    show_document=t.ShowDocumentClientCapabilities(support=True)
                ),
                text_document=t.TextDocumentClientCapabilities(
                    references=t.ReferenceClientCapabilities(dynamic_registration=True),
                    color_provider=t.DocumentColorClientCapabilities(dynamic_registration=True),
                    publish_diagnostics=t.PublishDiagnosticsClientCapabilities()
                ))
            return r

    # def on_initialize(self):
    #     rt = super(PythonCodeWidget, self).on_initialize()
    #     return rt

    # def on_textdocumentreferences(self, word: str, line, col):
    #     pass

    # def onTextDocumentHover(self, word: str, line: int, col: int):
    #
    #     def _infer():
    #         script = jedi.Script(self.code.text(), path=self.file_path())
    #         refs = script.infer(line + 1, col + 1)
    #         return refs
    #
    #     def _call(ret: List[Name]):
    #         for ref in ret:
    #             define_info = (ref.full_name or '').replace(word, '').rstrip('.')
    #             if ref.type == 'function':
    #                 describe = 'def ' + ref._get_docstring_signature()
    #             else:
    #                 describe = ref.description
    #             doc_string = ''.join(
    #                 [f'<p>{line_doc}</p>' for line_doc in ref.docstring(raw=True).splitlines(keepends=False)])
    #             hr_line = f'<hr>'
    #             full = f"""<p style="color:#49BDF8">{define_info}</p>{describe}\n{hr_line}{doc_string}"""
    #             if self.code.wordAtPoint(self.code.mapFromGlobal(QCursor.pos())):
    #                 self._render_tip(full, when_close=_when_close, line_str=describe)
    #             self.code.stop_hover = False
    #             return
    #
    #     def _when_close():
    #         try:
    #             self.code.stop_hover = False
    #         except:
    #             pass
    #
    #     def _err(error):
    #         try:
    #             print('error ', error)
    #             self.code.stop_hover = False
    #         except:
    #             import traceback
    #             traceback.print_exc()
    #
    #     position = self.code.positionFromLineIndex(line, col)
    #     hover_position = self.code.styleAt(position)
    #     if hover_position not in [
    #         StyledPythonLexer.NoWarning,
    #         StyledPythonLexer.Spaces,
    #         StyledPythonLexer.Operator,
    #         StyledPythonLexer.Tabs,
    #         StyledPythonLexer.TabsAfterSpaces,
    #         StyledPythonLexer.Number,
    #         StyledPythonLexer.Comment,
    #         StyledPythonLexer.CommentBlock,
    #         StyledPythonLexer.SingleQuotedString,
    #         StyledPythonLexer.SingleQuotedFString,
    #         StyledPythonLexer.DoubleQuotedString,
    #         StyledPythonLexer.DoubleQuotedFString,
    #         StyledPythonLexer.UnclosedString,
    #         StyledPythonLexer.TripleSingleQuotedString,
    #         StyledPythonLexer.TripleSingleQuotedFString,
    #         StyledPythonLexer.TripleDoubleQuotedString,
    #         StyledPythonLexer.TripleDoubleQuotedFString,
    #     ]:
    #         if self.code.stop_hover is False:
    #             self.code.stop_hover = True
    #             print('parse hover', hover_position)
    #             self.jedi_worker.add_task(_infer, call_back=_call, err_back=_err)
    #
    # def onTextDocumentReferences(self, word: str, line, col):
    #
    #     def _ref():
    #         script = jedi.Script(self.code.text(), path=self.file_path())
    #         refs = script.get_references(line + 1, col + 1, scope='file')
    #         return refs
    #
    #     def _call(ret: List[Name]):
    #         self.code.clearAllIndicators(self.code.indic_ref)
    #         self.code.clearAllIndicators(self.code.indic_ref_class)
    #         self.code.clearAllIndicators(self.code.indic_ref_define)
    #         self.code.current_refs.clear()
    #         current_file = (self.file_path() or '').replace('\\', '/')
    #         label, next_btn, pre_btn = self.peek_store_data('action')[0]
    #         if ret:
    #             label.setText(f' {len(ret)}个引用')
    #             next_btn.show()
    #             pre_btn.show()
    #         else:
    #             label.setText('')
    #             next_btn.hide()
    #             pre_btn.hide()
    #         for ref in ret:
    #             if ref.module_path and (ref.module_path.__str__().replace('\\', '/') == current_file):
    #                 # print('ref --> ', ref.type, ref.is_definition())
    #                 if ref.column is not None and ref.line is not None:
    #                     indic_type = self.code.indic_ref
    #                     if ref.is_definition() and ref.type == 'class':
    #                         indic_type = self.code.indic_ref_class
    #                     elif ref.is_definition():
    #                         indic_type = self.code.indic_ref_define
    #                     pos = self.code.positionFromLineIndex(ref.line - 1, ref.column)
    #                     self.code.setIndicatorRange(indic_type, pos, len(word))
    #                     self.code.current_refs.append(ref)
    #
    #     def _err(error):
    #         print('error --', error, self.code.stop_hover)
    #         self.code.stop_hover = False
    #
    #     position = self.code.positionFromLineIndex(line, col)
    #     hover_position = self.code.styleAt(position)
    #     if hover_position not in [
    #         StyledPythonLexer.NoWarning,
    #         StyledPythonLexer.Spaces,
    #         StyledPythonLexer.Operator,
    #         StyledPythonLexer.Tabs,
    #         StyledPythonLexer.TabsAfterSpaces,
    #         StyledPythonLexer.Number,
    #         StyledPythonLexer.Comment,
    #         StyledPythonLexer.CommentBlock,
    #         StyledPythonLexer.SingleQuotedString,
    #         StyledPythonLexer.SingleQuotedFString,
    #         StyledPythonLexer.DoubleQuotedString,
    #         StyledPythonLexer.DoubleQuotedFString,
    #         StyledPythonLexer.UnclosedString,
    #         StyledPythonLexer.TripleSingleQuotedString,
    #         StyledPythonLexer.TripleSingleQuotedFString,
    #         StyledPythonLexer.TripleDoubleQuotedString,
    #         StyledPythonLexer.TripleDoubleQuotedFString,
    #     ]:
    #         print('parse reference')
    #         self.jedi_worker.add_task(_ref, call_back=_call, err_back=_err)
    #     # self.onTextDocumentSyntaxCheck(word, line, col)
    #
    # def onTextDocumentRename(self, word: str, line, col):
    #     def confirm(renamed: str):
    #         print('rename check', renamed)
    #         local_cursor_point = self.code.local_pos
    #         current_value = self.code.verticalScrollBar().value()
    #         position = self.code.positionFromLineIndex(line, col)
    #         start = self.code.getIndicatorStartPos(self.code.indic_ref, position)
    #         word_length = len(word)
    #         self.code.replaceRange(start, word_length, renamed)
    #         for i in range(len(self.code.current_refs) - 1):
    #             if self.code.gotoNextIndicator(self.code.indic_ref, True):
    #                 next_start = self.code.getIndicatorStartPos(self.code.indic_ref, self.code.currentPosition() - 1)
    #                 if next_start is not None:
    #                     self.code.replaceRange(next_start, word_length, renamed)
    #
    #         self.code.verticalScrollBar().setValue(current_value)
    #         nl, nc = self.code.lineIndexFromPoint(local_cursor_point)
    #         self.code.setCursorPosition(nl, nc)
    #
    #     self._render_rename(word, confirm)
    #
    # def onTextDocumentInfer(self, word: str, line, col):
    #
    #     def _infer():
    #         script = jedi.Script(self.code.text(), path=self.file_path())
    #         refs = script.infer(line + 1, col + 1)
    #         return refs
    #
    #     def _goto_file(ref: Name, timer: QTimer):
    #         try:
    #             signal_manager.emit(signal_manager.openFileAndMoveCursor, ref.module_path.__str__(),
    #                                 ref.line - 1, ref.column - 1
    #                                 )
    #
    #         finally:
    #             self.code._has_alt_control = False
    #             timer.stop()
    #
    #     def _call(ret: List[Name]):
    #         current_file = (self.file_path() or '').replace('\\', '/')
    #         print('ret ====', ret)
    #         for ref in ret:
    #             self._timer = QTimer()
    #             self._timer.timeout.connect(lambda: _goto_file(ref, self._timer))
    #             self._timer.start(150)
    #             break
    #
    #     def _err(error):
    #         print('error --', error)
    #
    #     print('infer --', word, line, col)
    #     self.jedi_worker.add_task(_infer, call_back=_call, err_back=_err)
    #
    # def onTextDocumentSyntaxCheck(self, word: str, line, col):
    #
    #     def _syntax_check():
    #         script = jedi.Script(self.code.text(), path=self.file_path())
    #         refs = script.get_syntax_errors()
    #         return refs
    #
    #     def _call(ret: List[errors.SyntaxError]):
    #         print('ret ====', ret)
    #         for error in ret:
    #             print('error ', error._parso_error.code, error._parso_error.message)
    #             # print(error.get_message(), error.line, error.column, error.until_line, error.until_column)
    #         # parso.normalizer.Issue
    #
    #     def _err(error):
    #         print('error --', error)
    #
    #     print('infer --', word, line, col)
    #     self.jedi_worker.add_task(_syntax_check, call_back=_call, err_back=_err)
