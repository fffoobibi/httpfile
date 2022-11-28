import types
from collections import deque

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor

from pyqt5utils.qsci.base import BaseCodeWidget
from widgets.base import PluginBaseMixIn


def _make_child(instance, lex_func, app_exit, app_start_up, custom_menu_support, custom_menu_policy, set_apis,
                find_self=None, render_style=None, multi_line=False):
    from widgets.mainwidget import MainWidget
    class BaseCodeChild(BaseCodeWidget, PluginBaseMixIn):
        file_styled = pyqtSignal()
        run_margin_signal = pyqtSignal(int)

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

        def __init__(self):
            super(BaseCodeChild, self).__init__()
            self.code_container = instance
            self.find_from = find_self
            self.setCaretLineAlwaysVisible(True)
            # self.setCaretForegroundColor(QColor('#FF6C37'))
            self.enableMultiCursorSupport()
            self.setAutoCompletionSource(self.AcsAPIs)
            self.setStyleSheet('BaseCodeChild{border:none}')  # QToolTip{background:red;color:white}')
            if instance is None:
                out = custom_menu_support(instance)
            else:
                out = custom_menu_support()
            if out:
                self.setContextMenuPolicy(Qt.CustomContextMenu)
                self.customContextMenuRequested.connect(custom_menu_policy)
            if multi_line:
                # from PyQt5 import QsciScintilla
                # self: QsciScintilla
                self.setWrapMode(self.SC_WRAP_CHAR)
                # self.setWrapMode(self.WrapNone)  # 自动换行。self.WrapWord是父类QsciScintilla的

        def __getattr__(self, item):
            return getattr(instance, item)

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


class _Queue(object):
    def __init__(self):
        self._queue = deque()
        self._pos = 0
        self._len = 0

    def current_pos(self):
        return self._pos

    def is_empty(self):
        return not bool(self._len)

    def first(self):
        return self._queue[0]

    def clear(self):
        self._queue.clear()
        self._pos = 0
        self._len = 0

    def append(self, v):
        self._queue.append(v)
        self._len += 1

    def next(self):
        self._pos += 1
        self._pos %= self._len
        return self._queue[self._pos]

    def previous(self):
        self._pos -= 1
        self._pos %= self._len
        return self._queue[self._pos]
