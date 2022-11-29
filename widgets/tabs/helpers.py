import types
from collections import deque

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QFontMetrics, QKeyEvent
from PyQt5.QtWidgets import QAction, QWidget, QHBoxLayout, QLineEdit, QButtonGroup, QPushButton, QLabel, QSpacerItem, QSizePolicy, QFrame, QShortcut

from pyqt5utils.qsci.base import BaseCodeWidget
from widgets.base import PluginBaseMixIn
from widgets.factorys import add_styled
from widgets.styles import current_styles


def _make_child(instance, lex_func, app_exit, app_start_up, custom_menu_support, custom_menu_policy, set_apis,
                find_self=None, render_style=None, multi_line=False, simple_search=False):
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
                self.code.indicatorDefine(self.code.INDIC_FULLBOX, self.search_result_indicator)
                self.code.setIndicatorForegroundColor(QColor(255, 95, 0, 80), self.search_result_indicator)

                self.code.indicatorDefine(self.code.INDIC_FULLBOX, self.search_result_active_indicator)
                self.code.setIndicatorForegroundColor(QColor(241, 26, 5, 70), self.search_result_active_indicator)

            def __search_file(self, st):
                if self.__search is False:
                    self.code.clearAllIndicators(self.search_result_indicator)
                    self.code.clearAllIndicators(self.search_result_active_indicator)
                    self.__search_count = 0
                    self.__search = True
                    self.__search_results.clear()
                    text: str = self.sender().text().strip()
                    if text:
                        flag = self.code.findFirstTarget(text, False, False, False, 0, 0)
                        if flag:
                            self.__search_count += 1
                            founded = self.code.getFoundTarget()  # position, len
                            self.code.setIndicatorRange(self.search_result_indicator, *founded)
                            self.__search_results.append(founded)
                        while flag:
                            flag = self.code.findNextTarget()
                            if flag:
                                self.__search_count += 1
                                founded = self.code.getFoundTarget()
                                self.code.setIndicatorRange(self.search_result_indicator, *founded)
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
                        self.code.clearAllIndicators(self.search_result_active_indicator)
                        founded = self.__search_results.next()
                        line, col = self.code.lineIndexFromPosition(founded[0])
                        self.move_to(line, col)
                        count = self.__search_count
                        current = self.__search_results.current_pos()
                        self.__search_display.setText(f'{current + 1} / {count}')
                        self.code.setFirstVisibleLine(line)
                        self.code.setIndicatorRange(self.search_result_active_indicator, *founded)

                        search_line.setFocus(True)
                        search_line.deselect()

                def _pre():
                    if not self.__search_results.is_empty():
                        self.code.clearAllIndicators(self.search_result_active_indicator)
                        founded = self.__search_results.previous()
                        line, col = self.code.lineIndexFromPosition(founded[0])
                        self.move_to(line, col)
                        count = self.__search_count
                        current = self.__search_results.current_pos()
                        self.__search_display.setText(f'{current + 1} / {count}')
                        self.code.setFirstVisibleLine(line)
                        self.code.setIndicatorRange(self.search_result_active_indicator, *founded)

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
                    this.setStyleSheet('#CodeSearch{background: %s;border:1px solid %s}'
                                       'QLineEdit{border:none;background:%s;color:%s;padding:2px 0px}'
                                       'QPushButton{background:transparent;padding:0px}'
                                       'QPushButton:hover{background: lightgray;border:none}' % (current_styles.background_darker, current_styles.border,
                                                                                                 current_styles.background_lighter, current_styles.foreground
                                                                                                 ))

                base_font = QFont('微软雅黑', 9)
                w = QWidget(self)

                w.setObjectName('CodeSearch')
                w.render_custom_style = types.MethodType(_render_custom_style, w)
                add_styled(w, 'custom-style')

                lay = QHBoxLayout(w)
                lay.setContentsMargins(1, 0, 1, 0)
                lay.setSpacing(0)

                search_line = QLineEdit()
                search_line.setClearButtonEnabled(True)
                search_line.textChanged.connect(self.__search_file)
                search_line.setStyleSheet('font-family:微软雅黑')
                search_line.returnPressed.connect(_next)
                search_line.keyPressEvent = types.MethodType(_keyPressEvent, search_line)

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

        def __init__(self):
            super(BaseCodeChild, self).__init__()
            self.code_container = instance
            self.find_from = find_self
            self.setCaretLineAlwaysVisible(True)

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
                self.setWrapMode(self.WrapCharacter)
            if simple_search:
                self.__search = False
                self.__search_count = 0
                self.__search_results = _Queue()
                self.__search_action = QShortcut('ctrl+f', self, member=self.__search_action_slot, context=Qt.WidgetShortcut)  # QAction()
                self.__search_widget, self.__search_line, self.__search_display = self.__create_search_widget()
                self.__search_widget.hide()
                self.__define_search_indicator()

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
