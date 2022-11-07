import json
import re
import time
from pathlib import Path
from types import MethodType
from typing import Any, Dict, List

import aiohttp
from PyQt5.QtCore import Qt, pyqtSignal, QSize, pyqtSlot, QEvent
from PyQt5.QtGui import QColor, QFont, QMouseEvent, QCursor, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolButton, QSpacerItem, QSizePolicy, QListWidget, \
    QListWidgetItem, QApplication, QLabel, QToolTip, QHBoxLayout, QPushButton, QLineEdit, QMenu, QActionGroup, QAction
from aiohttp import ClientResponseError, ClientSession
from cached_property import cached_property

from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.components.widgets.buttons import RotateIconButton
from pyqt5utils.qsci.lexers.http_file import HttpFileLexer, CustomStyles
from widgets.utils import ConfigProvider, ConfigKey
from . import register, TabCodeWidget
from ..signals import signal_manager


class HttpFileStyles(CustomStyles):
    request = 0  # 1, 0b0001
    header = 1  # 2, 0b0010
    data = 2  # 4, 0b0100
    response = 3
    key = 4
    request_url = 5
    splitter = 6
    black = 7
    section = 8
    chinese = 12
    output = 13
    variable = 14

    # font flags
    underline = 9
    italic = 10
    bold = 11

    @classmethod
    def generate_styles(cls) -> Dict[int, str]:
        dic = {}
        for k, v in cls.__members__.items():
            dic[v.value] = k
        return dic

    @classmethod
    def defaultColor(cls, style: int):
        if style == cls.request:
            return QColor('#000000')
        elif style == cls.header:
            return QColor('#7F0C82')  # 紫色
        elif style == cls.section:
            return QColor('#CC6600')
        elif style == cls.data:
            return QColor('#CC0000')
        elif style == cls.response:
            return QColor(Qt.black)
        elif style == cls.key:  # request keyword
            return QColor('red')
        elif style == cls.request_url:  # request url
            return QColor('blue')  # 橘色
        elif style == cls.splitter:  # splitter ###
            return QColor(Qt.gray)
        elif style == cls.black:
            return QColor(Qt.black)
        elif style == cls.output:
            return QColor('#2D8C00')
        elif style == cls.variable:
            return QColor(Qt.darkBlue)

    @classmethod
    def defaultPaper(cls, style: int):
        if style == cls.request:
            return QColor('#FFEECC')
        elif style == cls.black:
            return QColor(Qt.white)
        elif style == cls.output:
            return QColor('#EDFCED')

    @classmethod
    def defaultFont(cls, style: int, font: QFont):
        if style == cls.underline:
            font.setUnderline(True)
        if style == cls.bold:
            font.setBold(True)
        if style == cls.italic:
            font.setItalic(True)
        if style == cls.chinese:
            font = QFont('宋体', 10)
        if style == cls.request_url:
            font.setItalic(True)
        elif style == cls.key:
            font.setBold(True)
        elif style == cls.header:
            font.setItalic(True)
        elif style == cls.output:
            font.setItalic(True)
            font.setUnderline(True)
            font.setBold(True)
        elif style == cls.variable:
            font.setItalic(True)
            # font.setBold(True)
        return font


class TabHttpLexer(HttpFileLexer):
    styles_class = HttpFileStyles


def hook_code_mouseMoveEvent(self, a0: QMouseEvent) -> None:
    self.__class__.mouseMoveEvent(self, a0)
    point = a0.pos()
    position = self.positionFromPoint(point)
    if self.hasIndicator(self.lexer().url_indicator, position):
        QToolTip.showText(QCursor.pos(), 'ctrl+点击跳转网页')
    else:
        QToolTip.hideText()


@register(file_types=['http'])
class HTTPFileCodeWidget(TabCodeWidget):
    url_indicator_signal = pyqtSignal(int, int, int, int, str)  # line, index, position, value, text
    file_loaded_flag = False

    listview: QListWidget  # type hint
    listview_loading_btn: RotateIconButton  # type hint
    listview_ret_label: QLabel  # type hint

    item_value_role = Qt.UserRole
    item_line_role = Qt.UserRole + 1
    item_method_url_role = Qt.UserRole + 2
    item_max_line_role = Qt.UserRole + 3

    def __init__(self):
        super(HTTPFileCodeWidget, self).__init__()
        self.code.setMouseTracking(True)
        self.code.mouseMoveEvent = MethodType(hook_code_mouseMoveEvent, self.code)
        self.code.file_styled.connect(self._file_styled)
        self.code.run_margin_signal.connect(self._run_request)

    @cached_property
    def lexer(self) -> HttpFileLexer:
        return self.code.lexer()

    def set_lexer(self) -> Any:
        return TabHttpLexer(self)

    def add_url_item(self, line, col, position, value, text, max_lines: int = None):
        content = text.split(' ')
        method = content[0]
        url = ' '.join(content[1:]).strip()
        if value not in self.listview._item_values:
            listview = self.listview
            item = QListWidgetItem()
            item.setForeground(Qt.transparent)
            item.setText(f'{method} {url}')
            item.setData(self.item_value_role, value)
            item.setData(self.item_line_role, line)
            label = QLabel()
            label.setIndent(4)
            line_number = f'{line + 1}'.zfill(max_lines or 2)
            label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            label.setText(
                f'{line_number}. <font color="red" ><b>{method}</font></b> <font style="text-decoration:underline">{url}</font>', )
            # raw_text=f'{line_number}. {method} {url}')
            listview.addItem(item)
            listview.setItemWidget(item, label)
            listview._item_values.add(value)
            item.setSizeHint(QSize(40, label.fontMetrics().height() * 2))
        else:
            for i in range(self.listview.count()):
                QApplication.processEvents()
                item = self.listview.item(i)
                if item.data(Qt.UserRole) == value:
                    label = self.listview.itemWidget(item)
                    label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                    line_number = f'{line + 1}'.zfill(max_lines or 2)
                    label.setText(
                        f'{line_number}. <font color="red" ><b>{method}</font></b> <font style="text-decoration:underline">{url}</font>', )
                    # raw_text=f'{line_number}. {method} {url}')
                    return

    def go_to_indicator(self, item: QListWidgetItem):
        line = item.data(Qt.UserRole + 1)
        col = 0
        self.move_to(line, col)

    def set_code_widgets(self) -> List[QWidget]:
        def _create_current_path():
            current_file_path_dir = Path(self.file_path())
            file_name = current_file_path_dir.name
            create_file_path = current_file_path_dir.parent / f'{file_name}.env.json'
            return create_file_path.__str__()

        def _create_panel():
            handle_width = ConfigProvider.default(ConfigKey.general, 'vertical_width').value
            container = QWidget()
            container.setStyleSheet('QWidget{background: #F2F2F2;border:1px solid lightgray}'
                                    'QPushButton{border:none;color:#0083D8;font-family:微软雅黑}'
                                    'QPushButton:hover{color:darkorange}')
            lay = QHBoxLayout(container)
            lay.setSpacing(6)
            lay.setContentsMargins(8, 0, handle_width, 0)
            run_all_btn = QPushButton('运行文件中的所有请求')
            add_request_btn = QPushButton('添加请求')
            add_env_btn = QPushButton('添加环境变量')
            load_btn = QPushButton('从文件中导入')
            menu = QMenu()
            menu.addAction('txt中导入')
            StylesHelper.add_menu_style(menu)

            load_btn.setMenu(menu)
            run_all_btn.setCursor(Qt.PointingHandCursor)
            add_request_btn.setCursor(Qt.PointingHandCursor)
            add_env_btn.setCursor(Qt.PointingHandCursor)
            load_btn.setCursor(Qt.PointingHandCursor)
            lay.addWidget(run_all_btn)
            lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))

            lay.addWidget(load_btn)
            lay.addWidget(add_request_btn)
            lay.addWidget(add_env_btn)

            check = QPushButton()
            check.setText('输出内容')
            check_menu = QMenu()
            check_menu.installEventFilter(self)
            action_group = QActionGroup(self)
            action_group.setExclusive(False)
            ac1 = QAction('响应时间')
            ac2 = QAction('响应头')
            ac3 = QAction('响应体')
            ac1.setCheckable(True)
            ac2.setCheckable(True)
            ac3.setCheckable(True)
            check_menu.addAction(action_group.addAction(ac1))
            check_menu.addAction(action_group.addAction(ac2))
            check_menu.addAction(action_group.addAction(ac3))
            StylesHelper.add_menu_style(check_menu)
            check.setMenu(check_menu)
            lay.addWidget(check)

            add_env_btn.clicked.connect(lambda e: signal_manager.emit(signal_manager.createFileAndOpen,
                                                                      _create_current_path(),
                                                                      '{}'))
            container.setFixedHeight(add_env_btn.fontMetrics().height() * 2.4)
            return container

        if self.is_remote:
            return []
        return [_create_panel()]

    def set_splitter_widgets(self) -> List[QWidget]:
        def _fresh_indicators(loading):
            self.fresh_search_panel()

        def _panel_search():
            text = self.sender().text().strip()
            if text:
                flag = 0
                for i in range(self.listview.count()):
                    QApplication.processEvents()
                    item = self.listview.item(i)
                    label = self.listview.itemWidget(item)
                    txt = label.text()
                    if text in txt:
                        flag += 1
                        self.listview.setRowHidden(i, False)
                    else:
                        self.listview.setRowHidden(i, True)
                self.listview_ret_label.setText(f'{flag}条结果')

        def _line_blank(st):
            txt = self.sender().text().strip()
            if not txt:
                for i in range(self.listview.count()):
                    QApplication.processEvents()
                    self.listview.setRowHidden(i, False)
                self.listview_ret_label.clear()

        def _create_search_panel():
            container = QWidget()
            container.setStyleSheet('QPushButton{border:none;background:transparent;padding:2px}'
                                    'QPushButton:hover{background:lightgray}'
                                    'QLabel, QLineEdit{font-family:微软雅黑}')
            lay = QVBoxLayout(container)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(1)

            top_container = QWidget()
            top_lay = QHBoxLayout(top_container)
            top_lay.setContentsMargins(0, 0, 0, 0)
            top_lay.setSpacing(0)
            line = QLineEdit()
            line.setPlaceholderText(' 查找')
            line.setClearButtonEnabled(True)
            line.returnPressed.connect(_panel_search)
            line.textChanged.connect(_line_blank)
            top_lay.addWidget(line)
            top_lay.addSpacing(10)
            ret_label = QLabel()
            top_lay.addWidget(ret_label)
            top_lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))

            run_all_btn = QPushButton()
            run_all_btn.setIcon(QIcon(':/icon/icons_next.svg'))
            run_all_btn.setCursor(Qt.PointingHandCursor)
            run_all_btn.setToolTip('运行所有请求')
            top_lay.addWidget(run_all_btn)

            btn = RotateIconButton()
            btn.setIcon(':/icon/icon-refresh.svg')
            btn.setToolTip('刷新页面')
            btn.clicked.connect(_fresh_indicators)
            top_lay.addWidget(btn)

            cf_btn = QPushButton()
            cf_btn.setIcon(QIcon(':/icon/扳手.svg'))
            cf_btn.setToolTip('配置')
            top_lay.addWidget(cf_btn)

            lay.addWidget(top_container)
            listview = QListWidget()
            container.listview = listview
            container.btn = btn
            container.ret_label = ret_label
            lay.addWidget(listview)
            return container

        handler_color = ConfigProvider.default(ConfigKey.general, 'handler_color').value
        handler_background = ConfigProvider.default(ConfigKey.general, 'handler_background').value
        search_panel = _create_search_panel()
        self.listview_loading_btn = search_panel.btn
        self.listview_ret_label = search_panel.ret_label
        self.listview = search_panel.listview
        self.listview._item_values = set()
        self.url_indicator_signal.connect(self.add_url_item)
        self.listview.itemClicked.connect(self.go_to_indicator)
        StylesHelper.set_v_history_style_dynamic(self.listview, color=handler_color, background=handler_background)
        StylesHelper.set_h_history_style_dynamic(self.listview, color=handler_color, background=handler_background)
        return [search_panel]

    def set_splitter_factor(self, index):
        if index == 0:
            return 200
        if index == 1:
            self.splitter.setStretchFactor(1, 0)
            return 100

    def set_splitter_handle(self, index):
        if index == 1:
            handler = self.splitter.handle(1)
            handler.setCursor(Qt.SizeHorCursor)
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            button = QToolButton(handler)
            button.setArrowType(Qt.RightArrow)
            layout.addWidget(button)
            # layout.addSpacerItem(QSpacerItem(20, 20, vPolicy=QSizePolicy.Expanding))
            handler.setLayout(layout)

    # slots #
    def when_modify(self, position, modificationType, text, length, linesAdded,
                    line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded):
        super(HTTPFileCodeWidget, self).when_modify(position, modificationType, text, length, linesAdded, line,
                                                    foldLevelNow, foldLevelPrev, token, annotationLinesAdded)
        full = self.code.SC_MOD_INSERTTEXT | self.code.SC_MOD_DELETETEXT
        if ~modificationType & full == full:
            return
        code = self.code
        lexer = code.lexer()
        cline, col = self.code.lineIndexFromPosition(position)
        if code.hasIndicator(lexer.url_indicator, position - 1):
            line_text = code.text(cline)
            indicator_value = code.SendScintilla(code.SCI_INDICATORVALUEAT, lexer.url_indicator,
                                                 position - 1)
            self.url_indicator_signal.emit(cline, col, position - 1, indicator_value, line_text.strip())
        else:
            if linesAdded:
                pass

    @pyqtSlot()
    def _file_styled(self):
        if self.file_loaded_flag:
            self.fresh_search_panel()
            self.file_loaded_flag = False

    @pyqtSlot(int)
    def _run_request(self, line):
        url, method = self.lexer.runner._find_url_method(line)
        headers = self.lexer.runner._find_headers(line)
        ret = re.findall(r'{{.*?}}', url)
        if ret:
            real_url = url.replace('{{', '{').replace('}}', '}').strip().format(**self.get_env())
            self.run_request_async(real_url, method, headers)
        print('get ', url, method, headers)

    def run_request_async(self, url, method, headers, session: ClientSession = None):
        async def _run():
            async with aiohttp.ClientSession() as sess:
                run_time = time.time()
                async with sess.request(method, url, headers=headers) as resp:
                    try:
                        resp.raise_for_status()
                        text = await resp.text()
                        end_time = time.time()
                        return resp.headers, text, resp.status, end_time - run_time
                    except ClientResponseError as e:
                        raise e

        def call_back(ret):
            headers, text, status, run_time = ret
            print('headers: ', dict(**headers))
            print('status: ', status)
            print('run time', run_time)

        def err_back(error: ClientResponseError):
            print('request fail error')

        self.analyse_worker.add_coro(_run(), call_back, err_back)

    @cached_property
    def analyse_worker(self):
        return self.code.get_or_create_worker('analyse_worker')

    def fresh_search_panel(self, content: str = None):
        def run_in_worker():
            pattern = r'get|post|header|delete|patch|options(\s+?http[s]?://.*)'
            ret = []
            lexer = self.code.lexer()
            line_count = self.code.lines()
            for line in range(line_count):
                line_text = self.code.text(line)
                if re.findall(pattern, line_text, re.I):
                    position = self.code.positionFromLineIndex(line, 0)
                    end_position = self.code.lineEndPosition(line) - 1
                    value = self.code.getIndicatorValue(lexer.url_indicator, end_position)
                    ret.append((line, 0, position, value, line_text.strip()))
            return ret, line_count

        def call_back(ret):
            values, line_count = ret
            if values:
                self.listview.clear()
                self.listview._item_values.clear()
            for info in values:
                line, col, position, value, line_text = info
                self.add_url_item(line, col, position, value, line_text, len(f'{line_count}'))
            self.listview_loading_btn.stop()

        def err_back(error):
            self.listview_loading_btn.stop()

        self.analyse_worker.add_task(run_in_worker, call_back=call_back, err_back=err_back)

    def load_file(self, file_path, content: str = None):
        self.file_loaded_flag = True
        super().load_file(file_path, content)

    # utils
    def get_env(self) -> dict:
        def _current_env_path():
            current_file_path_dir = Path(self.file_path())
            file_name = current_file_path_dir.name
            file_path = current_file_path_dir.parent / f'{file_name}.env.json'
            return file_path

        file_path = _current_env_path()
        if file_path.exists():
            content = file_path.read_text('utf-8')
            try:
                ret = json.loads(content)
                return ret
            except:
                return {}
        return {}

    # filter
    def eventFilter(self, a0: 'QObject', a1: QEvent) -> bool:
        if isinstance(a0, QMenu):
            if a1.type() == QEvent.MouseButtonRelease:
                action = a0.actionAt(a1.pos())
                if action:
                    action.activate(QAction.Trigger)
                return True
        return super().eventFilter(a0, a1)
