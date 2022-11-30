import re
import aiohttp

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from PyQt5.QtCore import QModelIndex, Qt, QRectF
from PyQt5.QtGui import QStandardItem, QCursor, QStandardItemModel, QPainter, QTextOption
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QLineEdit, QMenu, QStyledItemDelegate, QStyle,
                             QHBoxLayout, QPushButton)

from pyqt5utils.components import Confirm
from pyqt5utils.components.styles import StylesHelper

from widgets.base import PluginBaseMixIn
from widgets.components import (VirtualFileSystemTreeView, DirFlag, RootUriFlag, FileUriFlag, FileNameFlag, ModifyFlag,
                                RootItemFlag)
from widgets.signals import signal_manager
from widgets.utils import ConfigProvider, ConfigKey
from . import register
from ..factorys import styled_factory
from ..styles import current_styles

WorkPathFlag = Qt.UserRole + 10


@register('远程连接', index=1, icon=':/icon/远程管理.svg')
class NetWorkFileSystemTreeView(VirtualFileSystemTreeView, PluginBaseMixIn, styled_factory('custom-style')):
    default_work_path: str = ConfigProvider.default(ConfigKey.left_control_virtualtree, 'work_path')
    single_step = ConfigProvider.default(ConfigKey.general, 'single_step')

    class _TreeViewDelegate(QStyledItemDelegate):
        def paint(self, painter: QPainter, option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
            data = index.data(RootItemFlag)
            super().paint(painter, option, index)
            if option.state & QStyle.State_HasFocus and data is None:
                option.font.setBold(True)
            if data is None:  # and option.state & QStyle.State_MouseOver:
                dt = index.data(ModifyFlag)
                if dt:
                    painter.setPen(Qt.darkGray)
                    text = NetWorkFileSystemTreeView.format_time(dt)
                    fm_width = option.fontMetrics.width(text)
                    display = index.data(FileNameFlag)
                    display_width = option.fontMetrics.width(display)
                    rect = option.rect
                    if fm_width + display_width > rect.width():
                        fm_width = rect.width() - display_width - 30
                        text = option.fontMetrics.elidedText(text, Qt.ElideRight, rect.width() - display_width - 30,
                                                             Qt.AlignRight)
                    painter.drawText(QRectF(rect.width() - fm_width, rect.y(), fm_width, rect.height()), text,
                                     QTextOption())

    def render_custom_style(self):
        bk = current_styles.background_lighter
        dk = current_styles.background_darker
        border = current_styles.border
        fr = current_styles.foreground
        handler = current_styles.handler
        self.setStyleSheet('QTreeView{background: %s; color: %s; border:1px solid %s}' % (
            bk, fr, border
        ))
        self.header_widget().setStyleSheet('#HeaderFrame{background: %s;color:%s}' % (
            dk, fr
        ))
        StylesHelper.set_v_history_style_dynamic(self, color=handler, background='transparent', width=10)
        StylesHelper.set_h_history_style_dynamic(self, color=handler, background='transparent', height=10)

    def after_init(self):
        self.init_header_bar()
        self.load_remote_from_local()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menu_policy)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(self.single_step.value)
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.horizontalScrollBar().setSingleStep(self.single_step.value)

    def init_header_bar(self):
        btn = self.add_header_item('', ':/icon/tianjia.svg', '添加新的地址')
        btn1 = self.add_header_item('', ':/icon/crosshairmiaozhun.svg', '选择打开的文件')
        btn2 = self.add_header_item('', ':/icon/24gf-shrinkVertical2.svg', '全部收起')
        btn3 = self.add_header_item('', ':/icon/24gf-expandVertical2.svg', '全部展开')
        btn4 = self.add_header_item('', ':/icon/shezhixitongshezhigongnengshezhishuxing.svg', '显示选项菜单')
        btn.clicked.connect(self.add_new_remote)
        btn2.clicked.connect(lambda e: self.collapseAll())
        btn3.clicked.connect(self.expandAll)

    ### menu
    def menu_policy(self):
        if self.model().rowCount():
            index = self.currentIndex()
            is_root_item = index.data(RootItemFlag)
            if is_root_item:
                model: QStandardItemModel = self.model()
                current_item = model.itemFromIndex(index)
                menu = QMenu()
                ac = menu.addAction('修改信息')
                ac1 = menu.addAction('开始连接')
                menu.addSeparator()
                act2 = menu.addAction('同步所有文件')
                act = menu.exec_(QCursor.pos())
                if act == ac:
                    self.alter_remote_info(current_item)
                elif act == ac1:
                    self.connect_remote_addr(current_item)
                elif act == act2:
                    pass

    def add_new_remote(self):
        def ok():
            if http_line.text() and name_line.text():
                http = http_line.text()
                name = name_line.text()
                if not http.startswith('http'):
                    http = f'http://{http}'
                addr, port = self._get_host_port(http)
                self.load_remote_addr(addr, port, name, work_line.text())

        content = QWidget()
        content.setStyleSheet('QLabel, QPushButton, QLineEdit{font-family:微软雅黑;padding-top:2px; padding-bottom:2px}')
        content_lay = QGridLayout(content)
        content_lay.addWidget(QLabel('地址'), 0, 0)
        http_line = QLineEdit()
        http_line.setPlaceholderText(' http://url:port')
        http_line.setClearButtonEnabled(True)
        content_lay.addWidget(http_line, 0, 1)
        content_lay.addWidget(QLabel('名称'), 1, 0)
        name_line = QLineEdit()
        name_line.setPlaceholderText(' 显示名称')
        name_line.setClearButtonEnabled(True)
        content_lay.addWidget(QLabel('保存路径'), 2, 0)
        content_lay.addWidget(name_line, 1, 1)

        work_f = QWidget()
        work_f_lay = QHBoxLayout(work_f)
        work_f_lay.setContentsMargins(0, 0, 0, 0)
        work_line = QLineEdit()
        work_line.setClearButtonEnabled(False)
        work_line.setText(self.default_work_path.value)
        work_line.setEnabled(False)
        work_line_btn = QPushButton()
        work_line_btn.setStyleSheet('QPushButton{border:none;background:transparent}')
        work_line_btn.setText('...')

        work_f_lay.addWidget(work_line)
        work_f_lay.addWidget(work_line_btn)
        content_lay.addWidget(work_f, 2, 1)

        Confirm.msg(title='添加新的连接', target=self, content=content, ok=ok)

    def alter_remote_info(self, root_item: QStandardItem):
        def ok():
            if http_line.text() and name_line.text():
                http = http_line.text()
                name = name_line.text()
                if not http.startswith('http'):
                    http = f'http://{http}'
                root_item.setData(http, RootUriFlag)
                root_item.setData(name, FileNameFlag)
                root_item.setToolTip(http)
                remote_log_key = self.config_name('remote_logs')
                remote_logs: dict = self.settings.value(remote_log_key, defaultValue={})
                remote_logs[remote_log_key] = [http, name]
                self.settings.setValue(remote_log_key, remote_logs)

        content = QWidget()
        content.setStyleSheet('QLabel, QLineEdit{font-family:微软雅黑;padding-top:2px; padding-bottom:2px}')
        content_lay = QGridLayout(content)
        content_lay.addWidget(QLabel('地址'), 0, 0)
        http_line = QLineEdit()
        http_line.setPlaceholderText(' http://url:port')
        http_line.setText(root_item.data(RootUriFlag))
        http_line.setClearButtonEnabled(True)
        content_lay.addWidget(http_line, 0, 1)
        content_lay.addWidget(QLabel('名称'), 1, 0)
        name_line = QLineEdit()
        name_line.setText(root_item.data(Qt.DisplayRole))
        name_line.setPlaceholderText(' 显示名称')
        name_line.setClearButtonEnabled(True)
        content_lay.addWidget(name_line, 1, 1)
        Confirm.msg(title='修改连接信息', target=self, content=content, ok=ok)

    def load_remote_from_local(self):
        def add_site_item(addr, port, name):
            item = QStandardItem()
            path = f'http://{addr}:{port}'
            self.add_api_root(path, name, item)

        remotes: dict = self.settings.value(self.config_name('remote_logs'), defaultValue={})
        for k, value in remotes.items():
            url, name, work_path = value
            addr, port = self._get_host_port(url)
            add_site_item(addr, port, name)

    def load_remote_addr(self, addr, port, name, work_path: str):
        item = QStandardItem()
        self.worker.add_coro(self._fetch_remote_data(addr, port, name, item, False, work_path),
                             call_back=self._fetch_call_back,
                             err_back=self._fetch_error)

    def connect_remote_addr(self, root_item: QStandardItem):
        name = root_item.data(FileNameFlag)
        url = root_item.data(RootUriFlag)
        work_path = root_item.data(WorkPathFlag) or self.default_work_path.value
        addr, port = self._get_host_port(url)
        self.worker.add_coro(self._fetch_remote_data(addr, port, name, root_item, True, work_path),
                             call_back=self._fetch_call_back,
                             err_back=self._fetch_error)

    async def _fetch_remote_data(self, addr, port, name, item, add_new, work_path):
        url = f'http://{addr}:{port}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                json = await resp.json()
                return json['data'], url, name, item, add_new, work_path

    def _fetch_call_back(self, ret_val):
        ret, http_path, name, _, add_new, work_path = ret_val
        self.clear_model()
        item = self.add_api_root(http_path, name)
        item.setData(datetime.now(), ModifyFlag)
        item.setData(work_path, WorkPathFlag)
        self.load_dir_to_root(item, ret, http_path)
        self.setHorizontalHeaderLabels('项目')
        remote_log_key = self.config_name('remote_logs')
        remote_logs: dict = self.settings.value(remote_log_key, defaultValue={})
        remote_logs[remote_log_key] = [http_path, name, remote_logs.get('work_path') or self.default_work_path.value]
        # create work path
        dir_name = re.sub(r'[+\-*/\\<>?:"|]', '_', http_path + name)
        path = Path(work_path) / dir_name
        if not path.exists():
            path.mkdir(parents=True)
        self.settings.setValue(remote_log_key, remote_logs)

    def _fetch_error(self, error):
        sm = signal_manager
        sm.emit(sm.warn, error, 2500)

    def click_slot(self, index: QModelIndex):
        pass

    #####
    def double_click_slot(self, index: QModelIndex):
        def _down_load_err(err):
            pass

        def _down_call_back(ret):
            text, url = ret
            signal_manager.emit(signal_manager.openUrlFile, url, text)

        display, url, is_dir = index.data(FileNameFlag), index.data(FileUriFlag), index.data(DirFlag)
        print('double ', 'display:', display, 'userrole:', url, 'userrole+1', is_dir)
        self.worker.add_coro(self._download(url, is_dir), _down_call_back, _down_load_err)

    async def _download(self, url, is_dir):
        if not is_dir:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    ret = await resp.text()
                    return ret, url
        return '', url

    ### utils
    def _get_host_port(self, url: str):
        """
        http://127.0.0.1:9999
        """
        parse = urlparse(url)
        return parse.hostname, parse.port

    def _get_item_work_dir(self, root_item: QStandardItem) -> Path:
        name = root_item.data(FileNameFlag)
        http_path = root_item.data(RootUriFlag)
        work_path = root_item.data(WorkPathFlag) or self.default_work_path.value
        dir_name = re.sub(r'[+\-*/\\<>?:"|]', '_', http_path + name)
        return Path(work_path) / dir_name

    @classmethod
    def _display_time(cls, seconds, granularity=2):
        intervals = (
            ('周', 604800),  # 60 * 60 * 24 * 7
            ('天', 86400),  # 60 * 60 * 24
            ('小时', 3600),  # 60 * 60
            ('分', 60),
            ('秒', 1),
        )
        result = []
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result[:granularity])

    @classmethod
    def format_time(cls, time: datetime) -> str:
        time_delta = datetime.now() - time
        return f'(更新于{time.strftime("%m/%d %H:%M:%S")})'

    ###
    def when_app_exit(self, main_app):
        config_key = self.config_name('width')
        if self.width() != 640:
            self.settings.setValue(config_key, self.width())

    def when_app_start_up(self, main_app):
        config_key = self.config_name('width')
        default = self.settings.value(config_key)
        sm = main_app.sm
        if default is not None:
            sm.emit(sm.changeSplitSize, default, 10)
