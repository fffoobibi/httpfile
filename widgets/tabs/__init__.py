from collections import deque
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import List

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QColor
from PyQt5.QtWidgets import (QAction, QWidget, QHBoxLayout, QLineEdit, QButtonGroup, QPushButton, QSpacerItem,
                             QSizePolicy, QFrame, QVBoxLayout, QSplitter, QLabel)
from cached_property import cached_property

from pyqt5utils.components import Toast
from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.qsci.base import BaseCodeWidget
from widgets.base import PluginBaseMixIn
from widgets.signals import signal_manager
from widgets.utils import ConfigProvider, ConfigKey

__all__ = ('register', 'TabCodeWidget')

tab_codes = {}


def register(file_types: list):
    def wrapper(clz):
        tab_codes[clz] = [f'{f} File' if f else 'File' for f in file_types]
        return clz

    return wrapper


def load_tab_widgets():
    from pathlib import Path
    from importlib import import_module
    dir_path = Path(__file__).parent
    for path_ in dir_path.iterdir():
        if path_.name.startswith('tab_'):
            file, _ = path_.name.split('.')
            import_module(f'.{file}', 'widgets.tabs')
    return tab_codes


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


def _make_child(instance, lex_func, app_exit, app_start_up, custom_menu_support, custom_menu_policy):
    from widgets.mainwidget import MainWidget
    class BaseCodeChild(BaseCodeWidget, PluginBaseMixIn):
        file_styled = pyqtSignal()
        run_margin_signal = pyqtSignal(int)

        def __init__(self):
            super(BaseCodeChild, self).__init__()
            self.code_container = instance
            self.setCaretLineAlwaysVisible(True)
            self.setCaretForegroundColor(QColor('#FF6C37'))
            self.enableMultiCursorSupport()
            self.setAutoCompletionSource(self.AcsAPIs)
            self.setStyleSheet('BaseCodeChild{border:none}QToolTip{background:red;color:white}')
            out = custom_menu_support()
            if out:
                self.setContextMenuPolicy(Qt.CustomContextMenu)
                self.customContextMenuRequested.connect(custom_menu_policy)

        def __getattr__(self, item):
            return getattr(instance, item)

        def get_app(self) -> MainWidget:
            return super(BaseCodeChild, self).get_app()

        def set_lexer(self):
            return lex_func.__func__(self)

        def when_app_exit(self, main_app):
            return app_exit.__func__(self, main_app)

        def when_app_start_up(self, main_app):
            return app_start_up.__func__(self, main_app)

    return BaseCodeChild


class TabCodeWidget(QWidget):
    vertical = ConfigProvider.default(ConfigKey.general, 'vertical_width')
    horizontal = ConfigProvider.default(ConfigKey.general, 'horizontal_height')

    search_result_indicator = 20
    search_result_active_indicator = 21

    def after_init(self):
        pass

    def custom_menu_support(self):
        return False

    def custom_menu_policy(self, pos):
        pass

    def set_lexer(self):
        pass

    def when_app_exit(self, main_app):
        pass

    def when_app_start_up(self, main_app):
        pass

    @property
    def is_remote(self):
        return self._is_remote

    @is_remote.setter
    def is_remote(self, v: bool):
        self._is_remote = v

    @property
    def update_time(self) -> str:
        return self._update_time or ''

    @update_time.setter
    def update_time(self, v: str):
        self._update_time = v

    def load_file(self, file_path, content: str = None):
        if not self.is_remote:
            self._file = file_path
            return self.code.load_file(file_path)
        else:
            self._file = file_path
            return self.code.load_content(content)

    def file_path(self) -> str:
        return getattr(self, '_file', '')

    def move_to(self, line, col, focus=True):
        if line >= self.code.lines() - 1:
            line = self.code.lines()
        if focus:
            self.code.setFocus()
        self.code.ensureLineVisible(line)
        self.code.setCursorPosition(line, col)
        self.code.update()

    def set_read_only(self, v):
        self.code.setReadOnly(v)

    def __init__(self):
        super(TabCodeWidget, self).__init__()
        self.__main_lay = QHBoxLayout(self)
        self.__main_lay.setContentsMargins(0, 0, 0, 0)
        self.__main_lay.setSpacing(1)

        self.splitter = QSplitter(self)
        self.splitter.setHandleWidth(15)

        self.__code_container = QWidget(self)
        self.lay = QVBoxLayout(self.__code_container)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(1)

        self.code = _make_child(self, self.set_lexer, self.when_app_exit, self.when_app_start_up, self.custom_menu_support, self.custom_menu_policy)()

        StylesHelper.set_v_history_style_dynamic(self.code, color='#CFCFCF', background='transparent',
                                                 width=self.vertical.value)
        StylesHelper.set_h_history_style_dynamic(self.code, color='#CFCFCF', background='transparent',
                                                 height=self.horizontal.value)
        self._is_remote = False
        self._update_time = None
        self.__search = False
        self.__search_count = 0
        self.__search_results = _Queue()
        self.__search_action = QAction()
        self.__search_action.setShortcut('ctrl+f')
        self.__search_action.triggered.connect(self.__search_action_slot)
        self.__search_widget, self.__search_line, self.__search_display = self.__create_search_widget()
        self.__search_widget.hide()

        self.__save_action = QAction()
        self.__save_action.setShortcut('ctrl+s')
        self.__save_action.triggered.connect(self.__auto_save_slot)

        self.__cut_action = QAction()
        self.__cut_action.setShortcut('ctrl+x')
        self.__cut_action.triggered.connect(self.__cut_slot)

        self.__copy_action = QAction()
        self.__copy_action.setShortcut('ctrl+c')
        self.__copy_action.triggered.connect(self.__copy_slot)

        self.lay.addWidget(self.__search_widget)
        for w in self.set_code_widgets():
            self.lay.addWidget(w)
        self.lay.addWidget(self.code)

        self.addAction(self.__search_action)
        self.addAction(self.__save_action)
        self.addAction(self.__cut_action)

        self.code.cursor_signal.connect(self.__update_line_col)
        self.code.SCN_MODIFIED.connect(self.when_modify)
        self.code.SCN_MODIFYATTEMPTRO.connect(self.__show_information)

        self.__main_lay.addWidget(self.splitter)
        self.splitter.addWidget(self.__code_container)

        for widget in self.set_splitter_widgets():
            self.splitter.addWidget(widget)

        # self.splitter.setSizes([200, 100])
        for i in range(1, self.splitter.count()):
            self.set_splitter_handle(i)
        splitter_size = []
        for i in range(self.splitter.count()):
            size = self.set_splitter_factor(i)
            splitter_size.append(size)
        self.splitter.setSizes(splitter_size)

        # define search indicator
        self.__define_search_indicator()
        self.after_init()

    @cached_property
    def main_app(self):
        return self.code.get_app()

    @cached_property
    def toast(self):
        t = Toast.make_text('只读模式', self.code, keep=False, width=None)
        return t

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
        with suppress(Exception):
            self.toast.close()

    def hideEvent(self, a0) -> None:
        super().hideEvent(a0)
        with suppress(Exception):
            self.toast.hide()

    def when_modify(self, position, modificationType, text, length, linesAdded,
                    line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded):
        full = self.code.SC_MOD_INSERTTEXT | self.code.SC_MOD_DELETETEXT
        if ~modificationType & full == full:
            return

    def __show_information(self):
        point = self.code.getGlobalCursorPosition()
        point = self.code.mapToGlobal(point)
        point.setY(point.y() - 40)
        point.setX(point.x() - self.toast.width() / 2)
        self.toast.move(point)
        self.toast.show()

    def __update_line_col(self, line, col):
        signal_manager.emit(signal_manager.statusLineInfo, line, col)

    def __cut_slot(self):
        if not self.code.hasSelection():
            width = self.code.lineLength(self.code._current_line)
            self.code.setSelection(self.code._current_line, 0, self.code._current_line, width - 1)
            self.code.cut()
        else:
            self.code.cut()

    def __copy_slot(self):
        if not self.code.hasSelection():
            width = self.code.lineLength(self.code._current_line)
            self.code.setSelection(self.code._current_line, 0, self.code._current_line, width - 1)
            self.code.copy()
        else:
            self.code.copy()

    def __auto_save_slot(self):
        if self.file_path() and not self.is_remote:
            try:
                Path(self._file).write_text(self.code.text(), encoding='utf-8')
                save_time = datetime.now()
                msg = f'{self.file_path()} 已保存, {save_time.strftime("%H:%M:%S")}'
                signal_manager.emit(signal_manager.statusMsg, msg, 3)
            except:
                pass

    def __define_search_indicator(self):
        self.code.indicatorDefine(self.code.INDIC_FULLBOX, self.search_result_indicator)
        self.code.setIndicatorForegroundColor(QColor(255, 95, 0, 80), self.search_result_indicator)

        self.code.indicatorDefine(self.code.INDIC_FULLBOX, self.search_result_active_indicator)
        self.code.setIndicatorForegroundColor(QColor(241, 26, 5, 70), self.search_result_active_indicator)
        # self.code.setIndicatorOutlineColor(QColor('#FF5F00'))

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

        base_font = QFont('微软雅黑', 9)
        w = QWidget(self)
        w.setObjectName('CodeSearch')
        w.setStyleSheet('#CodeSearch{background: white;border:1px solid lightgray}'
                        'QLineEdit{border:none}'
                        'QPushButton{background:transparent}'
                        'QPushButton:hover{background: lightgray;border:none}')
        lay = QHBoxLayout(w)
        lay.setContentsMargins(2, 0, 2, 0)

        search_line = QLineEdit()
        search_line.setClearButtonEnabled(True)
        search_line.textChanged.connect(self.__search_file)
        search_line.setStyleSheet('font-family:微软雅黑')
        search_line.returnPressed.connect(_next)
        search_line.setFocusPolicy(Qt.ClickFocus)
        search_line.setMinimumWidth(search_line.fontMetrics().width('a' * 30))

        lay.addWidget(search_line)
        groups = QButtonGroup()

        c_btn = QPushButton()
        c_btn.setIcon(QIcon(':/icon/zifuxiao.svg'))
        r_btn = QPushButton()
        r_btn.setIcon(QIcon(':/icon/zhengzeshi.svg'))

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
        lay.addWidget(display_label)

        lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))

        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame.setStyleSheet('QFrame{background: transparent}')
        frame_lay = QHBoxLayout(frame)
        frame_lay.setContentsMargins(0, 0, 0, 0)
        frame_lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
        close_btn = QPushButton()
        close_btn.setIcon(QIcon(':/icon/guanbi.svg'))
        close_btn.clicked.connect(_close_policy)
        frame_lay.addWidget(close_btn)
        lay.addWidget(frame)
        w.setFixedHeight(QFontMetrics(QFont('微软雅黑', 10)).height() * 1.5)
        return w, search_line, display_label

    def set_splitter_factor(self, index) -> int:
        return 200

    def set_splitter_handle(self, index):
        pass

    def set_splitter_widgets(self) -> List[QWidget]:
        return []

    def set_code_widgets(self) -> List[QWidget]:
        return []
