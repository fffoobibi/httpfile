import json
import re
import time
from datetime import datetime
from pathlib import Path
from types import MethodType
from typing import Any, Dict, List

import aiohttp
from PyQt5.QtCore import Qt, pyqtSignal, QSize, pyqtSlot, QEvent, QPoint
from PyQt5.QtGui import QColor, QFont, QMouseEvent, QCursor, QIcon, QPixmap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QToolButton, QSpacerItem, QSizePolicy, QListWidget,
                             QListWidgetItem, QApplication, QLabel, QToolTip, QHBoxLayout, QPushButton, QLineEdit,
                             QMenu, QActionGroup, QAction)
from aiohttp import ClientSession
from cached_property import cached_property

from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.components.widgets.buttons import RotateIconButton
from pyqt5utils.qsci.base import BaseCodeWidget
from pyqt5utils.qsci.lexers.http_file import HttpFileLexer, CustomStyles
from widgets.signals import signal_manager
from widgets.utils import ConfigProvider, ConfigKey
from . import register, TabCodeWidget
from ..hooks import http_hooks
from ..styles import current_styles
from ..types import Request


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
        styles = current_styles.editor_http_file
        if style == cls.request:
            return QColor(styles['color'].get('request') or '#000000')
        elif style == cls.header:
            return QColor(styles['color'].get('header') or '#7F0C82')  # 紫色
        elif style == cls.section:
            return QColor(styles['color'].get('section') or '#CC6600')
        elif style == cls.data:
            return QColor(styles['color'].get('data') or '#CC0000')
        elif style == cls.response:
            return QColor(styles['color'].get('response') or '#7F0C82') #紫色
        elif style == cls.key:  # request keyword
            return QColor(styles['color'].get('key') or 'red')
        elif style == cls.request_url:  # request url
            return QColor(styles['color'].get('request_url') or 'blue')  # 橘色
        elif style == cls.splitter:  # splitter ###
            return QColor(styles['color'].get('splitter') or Qt.gray)
        elif style == cls.black:
            return QColor(styles['color'].get('black') or Qt.black)
        elif style == cls.output:
            return QColor(styles['color'].get('output') or '#2D8C00')
        elif style == cls.variable:
            return QColor(styles['color'].get('variable') or Qt.darkBlue)

    @classmethod
    def defaultPaper(cls, style: int):
        styles = current_styles.editor_http_file
        if style == cls.request:
            return QColor(styles['paper'].get('request') or '#FFEECC')
        elif style == cls.black:
            return QColor(styles['paper'].get('black') or Qt.white)
        elif style == cls.output:
            return QColor(styles['paper'].get('output') or '#EDFCED')
        return QColor(styles['paper'].get('request'))

    @classmethod
    def defaultFont(cls, style: int, font: QFont):
        styles = current_styles.editor_http_file
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
    pos = a0.pos()
    self: BaseCodeWidget
    parent: HTTPFileCodeWidget = self.code_container
    margin_0 = self.marginWidth(0)
    margin_1 = self.marginWidth(parent.run_margin_type)
    margin_2 = self.marginWidth(parent.info_margin_type)
    margin_3 = self.marginWidth(3)
    viewport = self.viewport()

    if pos.x() <= margin_0:
        if viewport.cursor().shape() != Qt.ArrowCursor:
            viewport.setCursor(Qt.ArrowCursor)
    elif margin_0 + margin_1 + margin_2 >= pos.x() > margin_0:
        if parent.line_has_marker(parent.run_margin_type, parent.run_margin_handle, pos):
            if viewport.cursor().shape() != Qt.PointingHandCursor:
                viewport.setCursor(Qt.PointingHandCursor)
        elif parent.line_has_marker(parent.info_margin_type, parent.success_marker_handle, pos):
            if viewport.cursor().shape() != Qt.PointingHandCursor:
                viewport.setCursor(Qt.PointingHandCursor)
        elif parent.line_has_marker(parent.info_margin_type, parent.fail_marker_handle, pos):
            if viewport.cursor().shape() != Qt.PointingHandCursor:
                viewport.setCursor(Qt.PointingHandCursor)
            # QToolTip.showText(pos, '请求失败', self)
            # Tips.pop('请求失败', self, place='t', dxy=pos)
        else:
            viewport.setCursor(Qt.ArrowCursor)
    elif margin_0 + margin_1 + margin_2 + margin_3 >= pos.x() > margin_0 + margin_1 + margin_2:
        if viewport.cursor().shape() != Qt.ArrowCursor:
            viewport.setCursor(Qt.ArrowCursor)
    else:
        self.__class__.mouseMoveEvent(self, a0)  # Qt.IBeamCursor
    position = self.positionFromPoint(pos)
    if self.hasIndicator(self.lexer().url_indicator, position):
        QToolTip.showText(QCursor.pos(), '跳转网页(ctrl + 点击)')
    else:
        QToolTip.hideText()


class _RunError(Exception):
    def __init__(self, line, raw, status, run_time, *args):
        super().__init__(*args)
        self.line = line
        self.raw = raw
        self.status = status
        self.run_time = run_time


@register(file_types=['http'])
class HTTPFileCodeWidget(TabCodeWidget):
    file_type = 'http'

    url_indicator_signal = pyqtSignal(int, int, int, int, str)  # line, index, position, value, text
    file_loaded_flag = False

    listview: QListWidget  # type hint
    listview_loading_btn: RotateIconButton  # type hint
    listview_ret_label: QLabel  # type hint

    item_value_role = Qt.UserRole
    item_line_role = Qt.UserRole + 1
    item_method_url_role = Qt.UserRole + 2
    item_max_line_role = Qt.UserRole + 3

    # configs
    output_headers = ConfigProvider.default(ConfigKey.http_code_widget, 'output_headers')
    output_response = ConfigProvider.default(ConfigKey.http_code_widget, 'output_response')
    output_runinfo = ConfigProvider.default(ConfigKey.http_code_widget, 'output_runinfo')

    # markers 0, 1, 2
    # margin_type 1, 2

    run_margin_type = 1
    run_margin_handle = 0
    run_margin_icon = ':/icon/运行，调试.svg'

    info_margin_type = 2
    success_marker_handle = 1
    success_marker_icon = ':/icon/成功.svg'

    fail_marker_handle = 2
    fail_marker_icon = ':/icon/感叹号.svg'

    def __init__(self):
        super(HTTPFileCodeWidget, self).__init__()
        self.code.setMouseTracking(True)
        self.code.mouseMoveEvent = MethodType(hook_code_mouseMoveEvent, self.code)
        self.code.file_styled.connect(self._file_styled)
        self.code.run_margin_signal.connect(self._run_request)
        self.define_code_markers()
        self.define_menus()
        if current_styles.editor_http_file.get('margin_color', None):
            self.code.setMarkerBackgroundColor(current_styles.editor_http_file.get('margin_color' or ))

    def define_menus(self):
        def _menu_policy(pos):
            m0 = self.code.marginWidth(0)
            m1 = self.code.marginWidth(self.run_margin_type)
            m2 = self.code.marginWidth(self.info_margin_type)

            menu = QMenu()
            StylesHelper.add_menu_style(menu)
            if self.line_has_marker(self.run_margin_type, self.run_margin_handle, pos) and m0 <= pos.x() <= m0 + m1:
                url, method = self.run_marker_url_info(pos)
                action = menu.addAction(f'运行 {url}')
                act = menu.exec_(QCursor.pos())
                if act == action:
                    line = self.code.lineAt(pos)
                    self.run_request_async_at_line(line)

            elif self.line_has_marker(self.info_margin_type, self.success_marker_handle, pos):
                pass
            elif self.line_has_marker(self.info_margin_type, self.fail_marker_handle, pos):
                pass

        self.code: QWidget
        self.code.setContextMenuPolicy(Qt.CustomContextMenu)
        self.code.customContextMenuRequested.connect(_menu_policy)

    def define_code_markers(self):
        editor = self.code

        editor.setMarginType(self.run_margin_type, editor.SymbolMargin)
        run_handle = editor.markerDefine(
            QPixmap(self.run_margin_icon).scaled(16, 16, transformMode=Qt.SmoothTransformation),
            self.run_margin_handle)
        editor.setMarginWidth(self.run_margin_type, 18)
        editor.setMarginSensitivity(self.run_margin_type, True)
        editor.setMarginMarkerMask(self.run_margin_type, 0b001)

        editor.setMarginType(self.info_margin_type, editor.SymbolMargin)
        success_handler = editor.markerDefine(
            QPixmap(self.success_marker_icon).scaled(16, 16, transformMode=Qt.SmoothTransformation),
            self.success_marker_handle)
        fail_handler = editor.markerDefine(
            QPixmap(self.fail_marker_icon).scaled(16, 16, transformMode=Qt.SmoothTransformation),
            self.fail_marker_handle)

        editor.setMarginWidth(self.info_margin_type, 18)
        editor.setMarginSensitivity(self.info_margin_type, True)
        editor.setMarginMarkerMask(self.info_margin_type, 0b110)

        # from PyQt5 import QsciScintilla
        # editor: QsciScintilla
        # fold margin
        editor.setFolding(editor.SC_FOLDDISPLAYTEXT_STANDARD, 3)
        editor.setMarginType(3, editor.SymbolMargin)
        # editor.setFoldMarginColors(Qt.red, Qt.red)
        # editor.setMarginsForegroundColor(Qt.red)
        # editor.setMarginsBackgroundColor(Qt.blue)
        # editor.setMarginWidth(3, '00')

        editor.marginClicked.connect(self.margin_slot)

    def line_has_marker(self, margin_type: int, marker_handler: int, pos: QPoint, line: int = None):
        margin_0 = self.code.marginWidth(0)
        margin_1 = self.code.marginWidth(self.run_margin_type)
        margin_2 = self.code.marginWidth(self.info_margin_type)
        current_line = line if line is not None else self.code.lineAt(pos)
        if current_line > -1:
            markers = self.code.markersAtLine(current_line)
            margin_lr = -1
            if pos.x() <= margin_0:
                return False
            elif margin_0 + margin_1 >= pos.x() > margin_0:  # marker 1
                margin_lr = 1
            elif margin_0 + margin_1 + margin_2 >= pos.x() > margin_0 + margin_1:  # marker 2
                margin_lr = 2
            if margin_lr == margin_type and (markers & (1 << marker_handler) == 1 << marker_handler):
                return True
        return False

    def margin_slot(self, margin_lr, line, state):
        # from PyQt5 import QsciScintilla
        editor = self.code
        margin_type = editor.markersAtLine(line)
        if margin_lr == self.run_margin_type and (margin_type & 0b001 == 0b001):
            editor.run_margin_signal.emit(line)
        elif margin_lr == self.info_margin_type and (margin_type & 0b010 == 0b010):  # 1 0b010
            print('success')
        elif margin_lr == self.info_margin_type and (margin_type & 0b100 == 0b100):  # 2 0b100
            print('fail')
        # print('margin type:', margin_lr, margin_type, state)
        # position = editor.positionFromLineIndex(line, 0)
        # style = editor.styleAt(position)
        # print('style: ', style)

    @cached_property
    def lexer(self) -> HttpFileLexer:
        return self.code.lexer()

    @cached_property
    def main_app(self):
        from widgets.mainwidget import MainWidget
        ret: MainWidget = self.code.get_app()
        return ret

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

        def _create_current_hook_path():
            current_file_path_dir = Path(self.file_path())
            file_name = current_file_path_dir.name
            create_file_path = current_file_path_dir.parent / f'{file_name}.hook.py'
            return create_file_path.__str__()

        def _create_panel():
            handle_width = ConfigProvider.default(ConfigKey.general, 'vertical_width').value
            container = QWidget()
            container.setStyleSheet('QWidget{background: #F2F2F2;border:1px solid lightgray}'
                                    'QPushButton{border:none;color:#0083D8;font-family:微软雅黑}'
                                    'QPushButton:hover{color:darkorange}')
            lay = QHBoxLayout(container)
            lay.setSpacing(10)
            lay.setContentsMargins(8, 0, handle_width, 0)
            run_all_btn = QPushButton('运行文件中的所有请求')
            add_request_btn = QPushButton('添加请求')

            add_env_btn = QPushButton('添加其他')
            menu = QMenu()
            env_action = menu.addAction('添加环境变量')
            hook_action = menu.addAction('添加hook')
            StylesHelper.add_menu_style(menu)
            add_env_btn.setMenu(menu)
            env_action.triggered.connect(lambda e: signal_manager.emit(signal_manager.createFileAndOpen,
                                                                       _create_current_path(),
                                                                       '{}'))
            hook_action.triggered.connect(lambda e: signal_manager.emit(signal_manager.createHookFileAndOpen,
                                                                        _create_current_hook_path(),
                                                                        http_hooks
                                                                        ))

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

            a1k = self.code.config_name('output_runinfo', self.__class__)
            a2k = self.code.config_name('output_headers', self.__class__)
            a3k = self.code.config_name('output_response', self.__class__)

            ac1_value = self.output_runinfo.value if self.code.settings.value(
                a1k) is None else self.code.settings.value(a1k)
            ac2_value = self.output_headers.value if self.code.settings.value(
                a2k) is None else self.code.settings.value(a2k)
            ac3_value = self.output_response.value if self.code.settings.value(
                a3k) is None else self.code.settings.value(a3k)

            ac1.setChecked(ac1_value)
            ac2.setChecked(ac2_value)
            ac3.setChecked(ac3_value)

            def action_trigger(key, ch):
                self.code.settings.setValue(key, ch)

            ac1.triggered.connect(lambda ch: action_trigger(a1k, ch))
            ac2.triggered.connect(lambda ch: action_trigger(a2k, ch))
            ac3.triggered.connect(lambda ch: action_trigger(a3k, ch))

            check_menu.addAction(action_group.addAction(ac1))
            check_menu.addAction(action_group.addAction(ac2))
            check_menu.addAction(action_group.addAction(ac3))
            StylesHelper.add_menu_style(check_menu)
            check.setMenu(check_menu)
            lay.addWidget(check)

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
        env = self.get_env()
        end_position = self.code.lineEndPosition(line) - 2
        url_value = self.code.getIndicatorValue(self.lexer.url_indicator, end_position)
        if ret:
            try:
                real_url = url.replace('{{', '{').replace('}}', '}').strip().format(**env)
                self.run_request_async(real_url, method, headers, line, url_value)
            except KeyError as e:
                keys = ','.join(e.args)
                msg = f'环境变量{keys}未设置!'
                signal_manager.emit(signal_manager.warn, msg, 3000)
        else:
            self.run_request_async(url, method, headers, line, url_value)

    def run_request_async_at_line(self, line: int):
        self._run_request(line)

    def run_request_async(self, url, method, headers, line, url_value, session: ClientSession = None):
        async def _run():
            async with aiohttp.ClientSession() as sess:
                run_time = time.time()
                try:
                    async with sess.request(method, url, headers=headers) as resp:
                        resp.raise_for_status()
                        text = await resp.text()
                        end_time = time.time()
                        return dict(**resp.headers), text, resp.status, end_time - run_time, url, method, line
                except Exception as e:
                    try:
                        status = resp.status
                    except:
                        status = None
                    end_time = time.time()
                    exc = _RunError(line, str(e), status, end_time - run_time)
                    raise exc

        def call_back(ret):
            headers, text, status, run_time, url, method, line = ret
            headers_text = '\n'.join([f'{k}: {v}' for k, v in headers.items()])
            request.status = status
            # add success marker
            self.code.markerAdd(line, self.success_marker_handle)

            self.main_app.show_bottom_panel(1)
            now = datetime.now().strftime('%H:%M:%S')
            title_msg = f'<font style="text-decoration:underline">{self.file_path()}</font>  ' \
                        f'<font color="red">{method.upper()}</font> <font style="color:blue">{url}</font> ' \
                        f'<font color="red"><b>{status} OK</b></font> <font color="gray">({now}, cost: {run_time:.4f}s)</font>'
            signal_manager.emit('api_server_update_request')
            signal_manager.emit('api_server_clear')
            signal_manager.emit('api_server_title', title_msg)
            signal_manager.emit('api_server_out_put', method.upper() + ' ' + url + f' {status} OK\n')
            signal_manager.emit('api_server_out_put', f'{headers_text}\n')
            signal_manager.emit('api_server_out_put', f'耗时: {run_time}\n')
            signal_manager.emit('api_server_out_put', text)
            signal_manager.emit('api_server_fold_all')

        def err_back(error: _RunError):
            line = error.line
            raw = error.raw
            status = error.status

            # add marker
            self.code.markerAdd(line, self.fail_marker_handle)
            request.status = status
            signal_manager.emit('api_server_update_request')
            signal_manager.emit('api_server_clear')
            signal_manager.emit('api_server_out_put', method.upper() + ' ' + url + f' {status} FAIL\n')
            signal_manager.emit('api_server_out_put', f'{error.raw}\n')
            signal_manager.emit('api_server_out_put', f'耗时: {error.run_time:.4f}s\n')

        request = Request(url=url, method=method, headers=headers, )
        signal_manager.emit('api_server_add_request', self.file_path(), url_value, request)
        self.analyse_worker.add_coro(_run(), call_back, err_back)

    @cached_property
    def analyse_worker(self):
        return self.code.get_or_create_worker('analyse_worker')

    def fresh_search_panel(self):
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
        """
        global env and self env
        :return:
        """

        def _current_env_path():
            current_file_path_dir = Path(self.file_path())
            file_name = current_file_path_dir.name
            file_path = current_file_path_dir.parent / f'{file_name}.env.json'
            return file_path

        def _global_env_path():
            return self.main_app.r_run_time.current

        global_path = _global_env_path() / 'http.global.env.json'
        if global_path.exists():
            global_content = global_path.read_text('utf-8')
            try:
                global_env = json.loads(global_content)
            except:
                global_env = {}
        else:
            global_env = {}
        file_path = _current_env_path()
        if file_path.exists():
            content = file_path.read_text('utf-8')
            try:
                self_env = json.loads(content)
            except:
                self_env = {}
        else:
            self_env = {}
        coped = dict(**global_env)
        coped.update(**self_env)
        return coped

    def line_content(self, pos: QPoint) -> str:
        line = self.code.lineAt(pos)
        if line > 0:
            return self.code.text(line)
        return ''

    def run_marker_url_info(self, pos) -> tuple:
        line = self.code.lineAt(pos)
        if self.line_has_marker(self.run_margin_type, self.run_margin_handle, pos):
            url, method = self.lexer.runner._find_url_method(line)
            env = self.get_env()
            if url.find('{{'):
                try:
                    true_url = url.replace('{{', '{').replace('}}', '}').format(**env)
                except:
                    true_url = url
                return true_url, method
            return url, method

    # filter
    def eventFilter(self, a0: 'QObject', a1: QEvent) -> bool:
        if isinstance(a0, QMenu):
            if a1.type() == QEvent.MouseButtonRelease:
                action = a0.actionAt(a1.pos())
                if action:
                    action.activate(QAction.Trigger)
                return True
        return super().eventFilter(a0, a1)
