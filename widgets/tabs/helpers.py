import collections
import inspect
import pprint
import types
import typing
import weakref
from collections import deque
from typing import Callable, Union, List

from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QTimer, QPoint
from PyQt5.QtGui import QColor, QFont, QIcon, QFontMetrics, QKeyEvent, \
    QMouseEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QButtonGroup, \
    QPushButton, QLabel, QFrame, QShortcut
from cached_property import cached_property
from lsprotocol.types import Diagnostic
from zope.interface import implementer

from lsp.lsp_interface import LanguageServerMixIn as IL
from lsp.utils import lsp_context
from pyqt5utils.qsci.base import BaseCodeWidget
from pyqt5utils.qsci.scintillacompat import QsciScintillaCompat
from widgets.base import PluginBaseMixIn
from widgets.factorys import add_styled
from widgets.interfaces import ILanguageInterFace
from widgets.styles import current_styles

_code_refs = weakref.WeakValueDictionary()


def get_code_refs():
    return _code_refs


@implementer(ILanguageInterFace)
class LanguageServerMixIn(object):
    support_language_parse: bool = False

    language_mask = 0
    rename_flag = 1
    infer_flag = 1 << 1
    completion_flag = 1 << 2
    hover_flag = 1 << 3
    ref_flag = 1 << 4
    syntax_flag = 1 << 5

    __setup_targets__ = [
        'onTextDocumentInfer', 'onTextDocumentCompletion',
        'onTextDocumentHover', 'onTextDocumentReferences',
        'onTextDocumentRename', 'onTextDocumentSyntaxCheck', 'capacities'
    ]

    __flags__ = 200

    def support_enabled(self, flags: int):
        self.language_mask |= flags

    def supported(self, flag: int):
        return self.language_mask & flag

    def support_disabled(self, flag: int):
        self.language_mask &= ~flag

    def set_up_from_obj(self, obj):
        clz = obj.__class__
        for k, v in clz.__dict__.items():
            if inspect.isfunction(v) and v.__name__ in self.__setup_targets__:
                bound_method = types.MethodType(v, self)
                setattr(self, k, bound_method)

    #### language server protocol ###

    def capacities(self) -> int:
        return 0

    def onInitialize(self):
        pass

    def onTextDocumentFormatting(self):
        pass

    def onTextDocumentDocumentHighlight(self):
        pass

    def onTextDocumentDocumentSymbol(self):
        pass

    def onTextDocumentFolding(self):
        pass

    def onTextDocumentDocumentLink(self):
        pass

    def onTextDocumentDidSave(self):
        pass

    def onTextDocumentSignatureHelp(self):
        pass

    def onTextDocumentDidChange(self, word: str, line, col):
        pass

    def onTextDocumentDidOpen(self, word: str, line, col):
        pass

    def onTextDocumentDidClose(self, word: str, line, col):
        pass

    def onTextDocumentInfer(self, word: str, line, col):
        pass

    def onTextDocumentCompletion(self, word: str, line, col):
        pass

    def onTextDocumentHover(self, word: str, line: int, col: int):
        pass

    def onTextDocumentReferences(self, word: str, line, col):
        pass

    def onTextDocumentRename(self, word: str, line, col):
        pass

    def onTextDocumentSyntaxCheck(self, word: str, line, col):
        pass


def _make_child(instance, lex_func, app_exit, app_start_up, custom_menu_support,
                custom_menu_policy, set_apis,
                find_self=None, render_style=None, multi_line=False,
                simple_search=False, cap=None,
                language_server_factory=IL
                ):
    from widgets.mainwidget import MainWidget
    class BaseCodeChild(BaseCodeWidget, PluginBaseMixIn,
                        language_server_factory):
        support_language_parse: bool = False

        click_signal = pyqtSignal()
        click_with_pos_signal = pyqtSignal(QPoint)
        file_styled = pyqtSignal()
        run_margin_signal = pyqtSignal(int)
        mouse_move_signal = pyqtSignal(str, int, int)
        indic_brace = 20

        indic_infer = 26
        indic_Completion = 27
        indic_hover = 28

        indic_ref = 29
        indic_ref_class = 25
        indic_ref_define = 24

        indic_rename = 30
        indic_diagnostics = 31  # error
        indic_diagnostics_warn = 21

        margins_count = 2

        if render_style:
            def render_custom_style(self):
                if isinstance(render_style, types.MethodType):
                    render_style.__func__(self)
                else:
                    render_style(self)

        if find_self:
            @property
            def code(self):
                return self

        if simple_search:
            search_result_indicator = 20
            search_result_active_indicator = 21

            def move_to(self, line, col, focus=True):
                if line >= self.code.lines() - 1:
                    line = self.code.lines()
                if focus:
                    self.code.setFocus()
                self.code.ensureLineVisible(line)
                self.code.setCursorPosition(line, col)
                self.code.update()

            def resizeEvent(self, *args, **kwargs):
                super().resizeEvent(*args, **kwargs)
                if self.__search_widget.isHidden() is False:
                    size = self.size()
                    w, h = size.width(), size.height()
                    fixed_width = min(w / 2, 200)
                    self.__search_widget.setFixedWidth(fixed_width)
                    self.__search_widget.move(w - fixed_width, 0)

            def __define_search_indicator(self):
                self.code.indicatorDefine(self.code.INDIC_FULLBOX,
                                          self.search_result_indicator)
                self.code.setIndicatorForegroundColor(QColor(255, 95, 0, 80),
                                                      self.search_result_indicator)

                self.code.indicatorDefine(self.code.INDIC_FULLBOX,
                                          self.search_result_active_indicator)
                self.code.setIndicatorForegroundColor(QColor(241, 26, 5, 70),
                                                      self.search_result_active_indicator)

            def __search_file(self, st):
                if self.__search is False:
                    self.code.clearAllIndicators(self.search_result_indicator)
                    self.code.clearAllIndicators(
                        self.search_result_active_indicator)
                    self.__search_count = 0
                    self.__search = True
                    self.__search_results.clear()
                    text: str = self.sender().text().strip()
                    if text:
                        flag = self.code.findFirstTarget(text, False, False,
                                                         False, 0, 0)
                        if flag:
                            self.__search_count += 1
                            founded = self.code.getFoundTarget()  # position, len
                            self.code.setIndicatorRange(
                                self.search_result_indicator, *founded)
                            self.__search_results.append(founded)
                        while flag:
                            flag = self.code.findNextTarget()
                            if flag:
                                self.__search_count += 1
                                founded = self.code.getFoundTarget()
                                self.code.setIndicatorRange(
                                    self.search_result_indicator, *founded)
                                self.__search_results.append(founded)
                    self.__search_display.setText(f'{self.__search_count}项结果')
                    if self.__search_count:
                        first = self.__search_results.first()
                        line, col = self.code.lineIndexFromPosition(first[0])
                        self.move_to(line, col, focus=False)
                    self.__search = False

            def __search_action_slot(self):
                if self.__search_widget.isHidden():
                    self.__search_widget.show()
                    self.__search_line.setFocus()
                    size = self.size()
                    w, h = size.width(), size.height()
                    fixed_width = min(w / 2, 200)
                    self.__search_widget.setFixedWidth(fixed_width)
                    self.__search_widget.move(w - fixed_width, 0)
                else:
                    self.__search_widget.hide()
                    self.__search_line.setFocus(False)

            def __create_search_widget(self):
                def _close_policy():
                    if w.isHidden():
                        w.show()
                    else:
                        w.hide()

                def _next():
                    if not self.__search_results.is_empty():
                        self.code.clearAllIndicators(
                            self.search_result_active_indicator)
                        founded = self.__search_results.next()
                        line, col = self.code.lineIndexFromPosition(founded[0])
                        self.move_to(line, col)
                        count = self.__search_count
                        current = self.__search_results.current_pos()
                        self.__search_display.setText(
                            f'{current + 1} / {count}')
                        self.code.setFirstVisibleLine(line)
                        self.code.setIndicatorRange(
                            self.search_result_active_indicator, *founded)

                        search_line.setFocus(True)
                        search_line.deselect()

                def _pre():
                    if not self.__search_results.is_empty():
                        self.code.clearAllIndicators(
                            self.search_result_active_indicator)
                        founded = self.__search_results.previous()
                        line, col = self.code.lineIndexFromPosition(founded[0])
                        self.move_to(line, col)
                        count = self.__search_count
                        current = self.__search_results.current_pos()
                        self.__search_display.setText(
                            f'{current + 1} / {count}')
                        self.code.setFirstVisibleLine(line)
                        self.code.setIndicatorRange(
                            self.search_result_active_indicator, *founded)

                        search_line.setFocus(True)
                        search_line.deselect()

                def _keyPressEvent(this, event: QKeyEvent):
                    if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_F:
                        w.hide()
                        self.code.setFocus()
                    elif event.key() == Qt.Key_Escape:
                        w.hide()
                        self.code.setFocus()
                    else:
                        this.__class__.keyPressEvent(this, event)

                def _render_custom_style(this):
                    this.setStyleSheet(
                        '#CodeSearch{background: %s;border:1px solid %s}'
                        'QLineEdit{border:none;background:%s;color:%s;padding:2px 0px}'
                        'QPushButton{background:transparent;padding:0px}'
                        'QPushButton:hover{background: lightgray;border:none}' % (
                            current_styles.background_darker,
                            current_styles.border,
                            current_styles.background_lighter,
                            current_styles.foreground
                        ))

                base_font = QFont('微软雅黑', 9)
                w = QWidget(self)

                w.setObjectName('CodeSearch')
                w.render_custom_style = types.MethodType(_render_custom_style,
                                                         w)
                add_styled(w, 'custom-style')

                lay = QHBoxLayout(w)
                lay.setContentsMargins(1, 0, 1, 0)
                lay.setSpacing(0)

                search_line = QLineEdit()
                search_line.setClearButtonEnabled(True)
                search_line.textChanged.connect(self.__search_file)
                search_line.setStyleSheet('font-family:微软雅黑')
                search_line.returnPressed.connect(_next)
                search_line.keyPressEvent = types.MethodType(_keyPressEvent,
                                                             search_line)

                lay.addWidget(search_line)
                groups = QButtonGroup()

                c_btn = QPushButton()
                c_btn.setIcon(QIcon(':/icon/zifuxiao.svg'))
                r_btn = QPushButton()
                r_btn.setIcon(QIcon(':/icon/zhengzeshi.svg'))
                c_btn.hide()
                r_btn.hide()

                p_btn = QPushButton()
                p_btn.setIcon(QIcon(':/icon/jiantou_liebiaoshouqi.svg'))
                p_btn.clicked.connect(_pre)
                p_btn.setFocusProxy(search_line)

                n_btn = QPushButton()
                n_btn.setIcon(QIcon(':/icon/jiantou_liebiaozhankai.svg'))
                n_btn.clicked.connect(_next)
                n_btn.setFocusProxy(search_line)

                groups.addButton(c_btn)
                groups.addButton(r_btn)

                lay.addWidget(c_btn)
                lay.addWidget(r_btn)
                lay.addWidget(p_btn)
                lay.addWidget(n_btn)

                display_label = QLabel()
                display_label.setFont(base_font)
                display_label.setText('0项结果')
                display_label.setStyleSheet('color:gray')

                display_label.hide()

                lay.addWidget(display_label)

                frame = QFrame()
                frame.setFrameShape(QFrame.NoFrame)
                frame.setStyleSheet('QFrame{background: transparent}')
                frame_lay = QHBoxLayout(frame)
                frame_lay.setContentsMargins(0, 0, 0, 0)

                close_btn = QPushButton()
                close_btn.setIcon(QIcon(':/icon/guanbi.svg'))
                close_btn.clicked.connect(_close_policy)
                frame_lay.addWidget(close_btn)
                lay.addWidget(frame)
                w.setFixedHeight(QFontMetrics(QFont('微软雅黑', 10)).height() * 1.5)
                return w, search_line, display_label

        def __getattr__(self, item):
            return getattr(instance, item)

        def __str__(self):
            return f'CodeEditor[{instance.file_type.upper()}]'

        __repr__ = __str__

        def statics_current_refs(self):
            return list(self._current_refs)

        @property
        def current_refs(self) -> Union[_Queue[t.Location], list]:
            if self.support_language_parse:
                return self._current_refs
            return []

        @property
        def current_diagnostics(self) -> Union[_Queue[t.Diagnostic], list]:
            if self.support_language_parse:
                return self._current_diagnostics
            return []

        @property
        def current_symbols(self) -> Union[
            _Queue[t.DocumentSymbol], _Queue[t.SymbolInformation], list]:
            if self.support_language_parse:
                return self._current_symbols
            return []

        @property
        def local_pos(self) -> QPoint:
            return self._current_pos

        def keyPressEvent(self, a0: QKeyEvent) -> None:
            super().keyPressEvent(a0)
            if a0.modifiers() & Qt.AltModifier:
                self._has_alt_control = True
            if a0.key() == Qt.Key_F1:
                if self.support_language_parse and self.supported(
                        self.rename_flag):
                    if self.hasIndicator(self.indic_ref,
                                         self.currentPosition()):
                        line, index = self.current_line_col
                        word = self.wordAtLineIndex(line, index)
                        self.onTextDocumentRename(word, line, index)
            if a0.key() == Qt.Key_Period:
                if self.support_language_parse and self.supported(
                        self.completion_flag):
                    line, index = self.current_line_col
                    word = self.wordAtLineIndex(line, index)
                    self.onTextDocumentCompletion(word, line, index,
                                                  self.code_container.file_path())

        def keyReleaseEvent(self, a0: QKeyEvent) -> None:
            super().keyReleaseEvent(a0)
            self._has_alt_control = False

        def mouseReleaseEvent(self, event: QMouseEvent) -> None:
            super(BaseCodeChild, self).mouseReleaseEvent(event)
            self.click_with_pos_signal.emit(event.pos())
            if event.pos().x() > self.get_invalid_margins_width():
                if self.support_language_parse and self.supported(
                        self.infer_flag):
                    self._current_pos = event.pos()
                    if self._has_alt_control and event.button() == Qt.LeftButton:
                        line, index = self.current_line_col
                        word = self.wordAtLineIndex(line, index)
                        if word:
                            self.onTextDocumentInfer(word, line, index)

        def get_invalid_margins_width(self):
            c = 0
            for i in range(self.margins_count + 1):
                c += self.marginWidth(i)
            return c

        def mouseMoveEvent(self, a0: QMouseEvent) -> None:
            if a0.pos().x() <= self.get_invalid_margins_width():
                self.viewport().setCursor(Qt.ArrowCursor)
            else:
                super().mouseMoveEvent(a0)
                if self.support_language_parse and self.supported(
                        self.hover_flag):
                    word = self.wordAtPoint(a0.pos())
                    line, index = self.lineIndexFromPoint(a0.pos())
                    if self._has_alt_control and word:
                        self.viewport().setCursor(Qt.PointingHandCursor)
                    else:
                        self.viewport().setCursor(Qt.IBeamCursor)
                    if word:
                        self.mouse_move_signal.emit(word, line, index)
                # else:
                #     super().mouseMoveEvent(a0)

        @pyqtSlot(QPoint)
        def _mouse_click_language_parse_event(self, pos: QPoint):
            if self.support_language_parse and pos.x() > self.get_invalid_margins_width():
                line, col = self.current_line_col
                word = self.wordAtLineIndex(line, col)
                pos = self.currentPosition()
                if self._has_alt_control and word and self.supported(
                        self.infer_flag):
                    self.onTextDocumentInfer(word, line, col)
                else:
                    flag = self.supported(self.ref_flag)
                    if word and flag:
                        if not any([self.hasIndicator(self.indic_ref, pos),
                                    self.hasIndicator(self.indic_ref_class,
                                                      pos),
                                    self.hasIndicator(self.indic_ref_define,
                                                      pos)
                                    ]):
                            self._current_refs.clear()
                            self.onTextDocumentReferences(word, line, col)
                    else:
                        if flag:
                            self._current_refs.clear()
                            self.clearAllIndicators(self.indic_ref)
                            self.clearAllIndicators(self.indic_ref_class)
                            self.clearAllIndicators(self.indic_ref_define)

        @pyqtSlot(str, int, int)
        def _mouse_hover_language_parse_event(self, word, line, col):
            pos = self.currentPosition()
            has_ref = any([self.hasIndicator(self.indic_ref, pos),
                           self.hasIndicator(self.indic_ref_class, pos),
                           self.hasIndicator(self.indic_ref_define, pos)
                           ])
            if word and not has_ref:
                self.onTextDocumentHover(word, line, col, instance.file_path())

        def __init__(self):
            super(BaseCodeChild, self).__init__()
            self.SendScintilla(self.SCI_SETFONTQUALITY,
                               self.SC_EFF_QUALITY_ANTIALIASED)

            self.code_container = instance
            self.find_from = find_self
            self._has_alt_control: bool = False
            self._hover_queue = deque(maxlen=2)
            self.stop_hover = False
            # language server capacities
            if cap:
                self.support_enabled(self.capacities())

            self.setCaretLineAlwaysVisible(True)
            self.enableMultiCursorSupport()
            self.setAutoCompletionSource(self.AcsAPIs)
            self.setStyleSheet(
                'BaseCodeChild{border:none}')  # QToolTip{background:red;color:white}')
            if instance is None:
                out = custom_menu_support(instance)
            else:
                out = custom_menu_support()
            if out:
                self.setContextMenuPolicy(Qt.CustomContextMenu)
                self.customContextMenuRequested.connect(custom_menu_policy)
            if multi_line:
                self.setWrapMode(self.WrapCharacter)
            if simple_search:
                self.__search = False
                self.__search_count = 0
                self.__search_results = _Queue()
                self.__search_action = QShortcut('ctrl+f', self,
                                                 member=self.__search_action_slot,
                                                 context=Qt.WidgetShortcut)  # QAction()
                self.__search_widget, self.__search_line, self.__search_display = self.__create_search_widget()
                self.__search_widget.hide()
                self.__define_search_indicator()

            self.click_with_pos_signal.connect(
                self._mouse_click_language_parse_event)
            self._current_refs = _Queue()
            self._current_diagnostics = _Queue()
            self._current_symbols = _Queue()
            self._current_pos = QPoint()

            _code_refs[id(self)] = self
            widget_debounce(self, self._mouse_hover_language_parse_event,
                            self.mouse_move_signal)

        def capacities(self) -> int:
            if hasattr(cap, '__func__'):
                return cap.__func__(self)
            return cap(self)

        def get_app(self) -> MainWidget:
            return super(BaseCodeChild, self).get_app()

        def set_lexer(self):
            if hasattr(lex_func, '__func__'):
                return lex_func.__func__(self)
            return lex_func(self)

        def when_app_exit(self, main_app):
            if hasattr(app_exit, '__func__'):
                return app_exit.__func__(self, main_app)
            return app_exit(self, main_app)

        def when_app_start_up(self, main_app):
            if hasattr(app_start_up, '__func__'):
                return app_start_up.__func__(self, main_app)
            return app_start_up(self, main_app)

        def set_apis(self):
            if hasattr(set_apis, '__func__'):
                return set_apis.__func__(self)
            return set_apis(self)

    return BaseCodeChild


T = typing.TypeVar('T')


class _Queue(typing.Generic[T]):

    def __init__(self):
        self._queue: typing.Deque[T] = deque()
        self._pos = 0
        self._len = 0

    def __len__(self) -> int:
        return self._len

    def __iter__(self):
        yield from self._queue

    def extend(self, seq: typing.Sequence[T]):
        self._queue.extend(seq)
        self._len += len(seq)

    def current_pos(self):
        return self._pos

    def is_empty(self):
        return not bool(self._len)

    def first(self) -> T:
        return self._queue[0]

    def clear(self):
        self._queue.clear()
        self._pos = 0
        self._len = 0

    def append(self, v):
        self._queue.append(v)
        self._len += 1

    def next(self) -> T:
        self._pos += 1
        self._pos %= self._len
        return self._queue[self._pos]

    def previous(self) -> T:
        self._pos -= 1
        self._pos %= self._len
        return self._queue[self._pos]


t = lsp_context.type
c = lsp_context.converter


class tab_code_context(object):
    def __init__(self, target):
        from . import TabCodeWidget
        self.target: TabCodeWidget = target

    def __enter__(self):
        return self.target

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class _LspHandlerHelper(object):
    @classmethod
    def get_position_range(cls, code: QsciScintillaCompat, t_range: t.Range) -> \
            typing.Tuple[int]:
        l1, c1 = t_range.start.line, t_range.start.character
        l2, c2 = t_range.end.line, t_range.end.character
        return code.positionFromLineIndex(l1, c1), code.positionFromLineIndex(
            l2, c2)


class LspResultProcessHandler(object):
    def __init__(self, tab):
        self.tab = tab
        if typing.TYPE_CHECKING:
            from . import TabCodeWidget
            self.tab: TabCodeWidget = tab

    def parse_uri(self, uri: str) -> str:
        return uri.strip('file:///').replace('\\', '/')

    def render_diagnostics(self, uri: str, diagnostics: List[Diagnostic]):
        parse_uri = self.parse_uri
        self = self.tab
        puri = parse_uri(uri)
        current_file = (self.file_path() or '').replace('\\', '/')
        self.code.clearAllIndicators(self.code.indic_diagnostics)
        self.code.current_diagnostics.clear()
        self.code.current_diagnostics.extend(diagnostics)

        if puri == current_file:
            error_count = 0
            warn_count = 0
            info_count = 0
            hint_count = 0
            for diagnostic in diagnostics:
                if diagnostic.severity == t.DiagnosticSeverity.Error:
                    error_count += 1
                    l1, c1 = diagnostic.range.start.line, diagnostic.range.start.character,
                    l2, c2 = diagnostic.range.end.line, diagnostic.range.end.character,
                    self.code.fillIndicatorRange(l1, c1, l2, c2,
                                                 self.code.indic_diagnostics)
                elif diagnostic.severity == t.DiagnosticSeverity.Warning:
                    warn_count += 1
                    print(diagnostic.source, diagnostic.code,
                          diagnostic.message)
                    l1, c1 = diagnostic.range.start.line, diagnostic.range.start.character,
                    l2, c2 = diagnostic.range.end.line, diagnostic.range.end.character,
                    self.code.fillIndicatorRange(l1, c1, l2, c2,
                                                 self.code.indic_diagnostics_warn)
                elif diagnostic.severity == t.DiagnosticSeverity.Information:
                    info_count += 1
                elif diagnostic.severity == t.DiagnosticSeverity.Hint:
                    hint_count += 1
            if self.file_type == 'python':
                _, __, ___, diag_error, diag_warn, diag_error_msg, diag_warn_msg, diagnostics_frame = \
                    self.peek_store_data('action')[0]
                if any([error_count, warn_count]):
                    diagnostics_frame.show()
                    msg = []
                    if error_count:
                        diag_error.show()
                        diag_error_msg.show()
                        diag_error_msg.setText(f'{error_count}')
                        msg.append(f'{error_count}个错误')
                    else:
                        diag_error.hide()
                        diag_error_msg.hide()
                    if warn_count:
                        msg.append(f'{warn_count}个警告')
                        diag_warn.show()
                        diag_warn_msg.show()
                        diag_warn_msg.setText(f'{warn_count}')
                    else:
                        diag_warn.hide()
                        diag_warn_msg.hide()
                    if msg:
                        diagnostics_frame.setToolTip(f'{",".join(msg)}')
                else:
                    diagnostics_frame.hide()

    def render_symbols(self, symbols: List[t.DocumentSymbol], line: int,
                       col: int, position: int):

        def find_symbol_pointer(sym: t.DocumentSymbol):
            sp = _LspHandlerHelper.get_position_range(self.tab.code, sym.range)
            pointers_ = []
            if sp[0] <= position <= sp[-1]:
                pointers_.append(sym.name)
                if not sym.children:
                    return pointers_
                else:
                    for ch in sym.children:
                        c_pointers = find_symbol_pointer(ch)
                        pointers_.extend(c_pointers)
            return pointers_

        # print('get symbols ,', len(symbols))
        if len(self.tab.code.current_symbols) == 0:
            self.tab.code.current_symbols.extend(symbols)
        pointers = []
        for symbol in symbols:
            pointers = find_symbol_pointer(symbol)
            if pointers:
                break
        self.tab.set_navigator_items(pointers)

    def render_references(self, ret: List[t.Location]):
        parse_uri = self.parse_uri
        self = self.tab
        # print('clas -----', self.code)
        self.code.clearAllIndicators(self.code.indic_ref)
        self.code.clearAllIndicators(self.code.indic_ref_class)
        self.code.clearAllIndicators(self.code.indic_ref_define)
        self.code.current_refs.clear()
        current_file = (self.file_path() or '').replace('\\', '/')
        label, next_btn, pre_btn, a1, a2, a3, a4, a5 = \
            self.peek_store_data('action')[0]

        l = 0
        for ref in ret:
            pri = parse_uri(ref.uri)
            if ref.uri and (pri.lower() == current_file.lower()):
                l += 1
                indic_type = self.code.indic_ref
                # if ref.is_definition() and ref.type == 'class':
                #     indic_type = self.code.indic_ref_class
                # elif ref.is_definition():
                #     indic_type = self.code.indic_ref_define
                # pos = self.code.positionFromLineIndex(ref.line - 1, ref.column)
                # self.code.setIndicatorRange(indic_type, pos, len(word))
                l1, c1 = ref.range.start.line, ref.range.start.character
                l2, c2 = ref.range.end.line, ref.range.end.character
                self.code.fillIndicatorRange(l1, c1, l2, c2, indic_type)
                self.code.current_refs.append(ref)
        if l:
            label.setText(f' {l}个引用')
            label.show()
            next_btn.show()
            pre_btn.show()
        else:
            label.setText('')
            label.hide()
            next_btn.hide()
            pre_btn.hide()

    def render_renames(self, results):
        pass

    def render_hover(self, results):
        pass

    def render_complete(self, results):
        pass

    def render_format(self, results: List[t.TextEdit]):
        for text in results:
            print(text.new_text)
            self.tab.code.setText(text.new_text)

        self.tab.code.onTextDocumentDidChange(
            self.tab.file_path(), self.tab.code.text(), 1
        )
        # end_line, end_col = self.tab.code.lineIndexFromPosition(
        #     self.tab.code.length())
        # self.tab.code.onTextDocumentPublishDiagnostics(self.tab.file_path(), 1,
        #                                                0, 0, end_line, end_col
        #                                                )


class StoreDataMixIn(object):

    @cached_property
    def _store_data(self):
        return collections.defaultdict(lambda: deque())

    def peek_store_data(self, key='default') -> deque:
        return self._store_data[key]

    def store_data(self, data, key='default'):
        self._store_data[key].append(data)

    def store_data_clear(self, key='default'):
        self._store_data[key].clear()

    def restore_data(self, key='default'):
        if len(self._store_data[key]):
            return self._store_data[key].pop()

    def restore_clear(self):
        self._store_data.clear()


def widget_debounce(self: QWidget, trigger_func: Callable,
                    trigger_signal: pyqtSignal, interval: int = 500) -> None:
    def _trigger(*a):
        self._debounce_args = a
        timer.stop()
        timer.start()

    def _wrapper():
        trigger_func(*self._debounce_args)

    debounce_name = f'_debounce_{trigger_func.__name__}_timer'
    timer = QTimer()
    timer.setSingleShot(True)
    timer.setInterval(interval)
    timer.timeout.connect(_wrapper)
    self._debounce_args = None
    self._debounce_timer = timer
    setattr(self, debounce_name, timer)
    trigger_signal.connect(_trigger)


def get_ref_line_words(refs: _Queue[t.Location], sci: QsciScintilla):
    # refs: List[Name]
    for ref in refs:
        yield ref, ref.uri.strip('file:///').replace('\\', '/').split('/')[-1]
        # line, col = ref.line - 1, ref.column
        # yield sci.text(line), sci.wordAtLineIndex(line, col), line, col, ref
