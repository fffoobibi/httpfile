import typing
from contextlib import suppress
from pathlib import Path
from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QIcon
from PyQt5.QtWidgets import (QAction, QWidget, QHBoxLayout, QLineEdit, QButtonGroup, QPushButton, QSpacerItem,
                             QSizePolicy, QFrame, QVBoxLayout, QSplitter)
from cached_property import cached_property

from pyqt5utils.components import Toast
from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.qsci.base import BaseCodeWidget
from widgets.base import PluginBaseMixIn
from widgets.signals import signal_manager
from widgets.utils import ConfigProvider, ConfigKey

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


def _make_child(instance, lex_func, app_exit, app_start_up):
    class BaseCodeChild(BaseCodeWidget, PluginBaseMixIn):
        file_styled = pyqtSignal()
        run_margin_signal = pyqtSignal(int)

        def __getattr__(self, item):
            return getattr(instance, item)

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

    def move_to(self, line, col):
        if line >= self.code.lines() - 1:
            line = self.code.lines()
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

        self.code = _make_child(self, self.set_lexer, self.when_app_exit, self.when_app_start_up)()
        self.code.setStyleSheet('BaseCodeWidget{border:none}QToolTip{background:red;color:white}')

        StylesHelper.set_v_history_style_dynamic(self.code, color='#CFCFCF', background='transparent',
                                                 width=self.vertical.value)
        StylesHelper.set_h_history_style_dynamic(self.code, color='#CFCFCF', background='transparent',
                                                 height=self.horizontal.value)
        self._is_remote = False
        self._update_time = None
        self.__search_action = QAction()
        self.__search_action.setShortcut('ctrl+f')
        self.__search_action.triggered.connect(self.__search_action_slot)
        self.__search_widget = self.__create_search_widget()
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
        # self.code.setReadOnly(True)
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
        # self.splitter.setStretchFactor(1, 0)
        # self.set_splitter_handle(1)

    @cached_property
    def toast(self):
        t = Toast.make_text('只读模式', self.code, keep=False, width=50)
        t.hide()
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
        if (~modificationType & full == full):
            return
        # point = self.code.getGlobalCursorPosition()
        # point = self.code.mapToGlobal(point)
        # point.setY(point.y() - 40)
        # self.toast.move(point)
        # self.toast.show()

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
        if self.file_path():
            try:
                Path(self._file).write_text(self.code.text(), encoding='utf-8')
            except:
                pass

    def __search_action_slot(self):
        if self.__search_widget.isHidden():
            self.__search_widget.show()
        else:
            self.__search_widget.hide()

    def __create_search_widget(self):
        def _close_policy():
            if w.isHidden():
                w.show()
            else:
                w.hide()

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
        lay.addWidget(search_line)
        groups = QButtonGroup()

        c_btn = QPushButton()
        c_btn.setIcon(QIcon(':/icon/zifuxiao.svg'))
        r_btn = QPushButton()
        r_btn.setIcon(QIcon(':/icon/zhengzeshi.svg'))

        p_btn = QPushButton()
        p_btn.setIcon(QIcon(':/icon/jiantou_liebiaoshouqi.svg'))
        n_btn = QPushButton()
        n_btn.setIcon(QIcon(':/icon/jiantou_liebiaozhankai.svg'))

        groups.addButton(c_btn)
        groups.addButton(r_btn)
        update_btn = QPushButton()
        lay.addWidget(c_btn)
        lay.addWidget(r_btn)
        lay.addWidget(p_btn)
        lay.addWidget(n_btn)
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

        w.search_line = search_line
        w.search_line.setMinimumWidth(search_line.fontMetrics().width('a' * 30))
        w.setFixedHeight(QFontMetrics(QFont('微软雅黑', 10)).height() * 1.5)
        return w

    def set_splitter_factor(self, index) -> int:
        return 200

    def set_splitter_handle(self, index):
        pass

    def set_splitter_widgets(self) -> List[QWidget]:
        return []

    def set_code_widgets(self) -> List[QWidget]:
        return []

    ###########################
    def set_lexer(self):
        pass

    def when_app_exit(self, main_app):
        pass

    def when_app_start_up(self, main_app):
        pass
