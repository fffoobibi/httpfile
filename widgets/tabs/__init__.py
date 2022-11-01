from pathlib import Path

from PyQt5.QtGui import QFont, QFontMetrics, QIcon
from PyQt5.QtWidgets import (QAction, QWidget, QHBoxLayout, QLineEdit, QButtonGroup, QPushButton, QSpacerItem,
                             QSizePolicy, QFrame, QVBoxLayout)

from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.qsci.base import BaseCodeWidget
from widgets.base import PluginBaseMixIn

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


def _make_child(instance, target, lex_func, app_exit, app_start_up):
    class BaseCodeChild(target, PluginBaseMixIn):

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

    def load_file(self, file_path):
        self._file = file_path
        self.code.load_file(file_path)

    def file_path(self) -> str:
        return getattr(self, '_file', '')

    def __init__(self):
        super(TabCodeWidget, self).__init__()
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(1)

        self.code = _make_child(self, BaseCodeWidget, self.set_lexer, self.when_app_exit, self.when_app_start_up)()
        self.code.setStyleSheet('border:none')

        StylesHelper.set_v_history_style_dynamic(self.code, color='#CFCFCF', background='transparent',
                                                 width=self.vertical.value)
        StylesHelper.set_h_history_style_dynamic(self.code, color='#CFCFCF', background='transparent',
                                                 height=self.horizontal.value)
        self.__search_action = QAction()
        self.__search_action.setShortcut('ctrl+f')
        self.__search_action.triggered.connect(self.__search_action_slot)
        self.__search_widget = self.__create_search_widget()
        self.__search_widget.hide()

        self.__save_action = QAction()
        self.__save_action.setShortcut('ctrl+s')
        self.__save_action.triggered.connect(self.__auto_save_slot)

        self.lay.addWidget(self.__search_widget)
        self.lay.addWidget(self.code)

        self.addAction(self.__search_action)
        self.addAction(self.__save_action)

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

    def set_lexer(self):
        pass

    def when_app_exit(self, main_app):
        pass

    def when_app_start_up(self, main_app):
        pass
