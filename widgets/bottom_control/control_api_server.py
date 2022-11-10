from pathlib import Path

from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex, QSize
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon, QPainter, QPixmap, QTransform
from PyQt5.QtWidgets import QWidget, QApplication, QStyledItemDelegate

from pyqt5utils.components.styles import StylesHelper
from ui.api_serverui import Ui_Form
from widgets.base import PluginBaseMixIn
from widgets.bottom_control import register
from widgets.signals import ProcessSignalMixInHelper, signal_manager
from widgets.types import Request
from widgets.utils import ConfigProvider, ConfigKey
from . import BottomWidgetMixIn


class ApiCodeWidget(QWidget):
    pass


@register(name='服务', icon=':/icon/服务01.svg', index=2)
class ApiControlWidget(QWidget, Ui_Form, BottomWidgetMixIn, PluginBaseMixIn, ProcessSignalMixInHelper):
    check_state_signal = pyqtSignal(bool)
    horizontal = ConfigProvider.default(ConfigKey.general, 'horizontal_height')
    vertical = ConfigProvider.default(ConfigKey.general, 'vertical_width')

    update_signal = pyqtSignal(QStandardItem, Request)

    class TreeViewItemDelegate(QStyledItemDelegate):
        def paint(self, painter: QPainter, option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
            super().paint(painter, option, index)
            data = index.data(Qt.UserRole)
            if data is not None:
                file_path, request, url_value = data
                rect = option.rect
                request: Request
                if request.status == -1:  # loading
                    pass

    def __init__(self):
        super(ApiControlWidget, self).__init__()
        self.setupUi(self)
        self.startTimer(40)
        self._angle = 0
        self._pixmap = QPixmap(':/icon/shuaxin.svg')
        self._pixmap_size = self._pixmap.size()
        self.update_signal.connect(self._update_slot)

    def _update_slot(self, item: QStandardItem, req: Request):
        if req.status == -1:
            item.setIcon(QIcon(self._get_rotate_picture()))
            # self.treeView.viewport().update()

    def _get_rotate_picture(self):
        pixmap = QPixmap(self._pixmap_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing, True)
        w, h = self._pixmap_size.width(), self._pixmap_size.height()
        painter.translate(w / 2, h / 2)
        painter.rotate(self._angle)
        painter.drawPixmap(-w / 2, -h / 2, self._pixmap)
        return pixmap

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        self._angle += 10
        self._angle %= 360
        for item in self.model_child_items:
            data = item.data(Qt.UserRole)
            if data:
                file_path, request, value = data
                if request.status == -1:
                    icon = QIcon(self._get_rotate_picture())
                    item.setIcon(icon)

    def after_init(self):
        def _set_title(st):
            self.label.setText(st)

        StylesHelper.set_v_history_style_dynamic(self.textBrowser.code_html.code, color='#CFCFCF',
                                                 background='transparent',
                                                 width=self.vertical.value)
        StylesHelper.set_h_history_style_dynamic(self.textBrowser.code_html.code, color='#CFCFCF',
                                                 background='transparent',
                                                 height=self.horizontal.value)

        def _tree_clicked(index: QModelIndex):
            ret = index.data(Qt.UserRole)
            if ret is not None:
                file_path, request, url_value = ret
                self.get_app().open_file(file_path, url_value - 1, 0)

        self.splitter.setSizes([200, 1000])
        self.splitter.setChildrenCollapsible(0)
        self.splitter.widget(0).setMinimumWidth(0)
        self.splitter.widget(1).setMinimumWidth(40)
        self.splitter.handle(1).setCursor(Qt.SizeHorCursor)

        self.pushButton_6.clicked.connect(self.wrap_slot)
        self.pushButton_7.clicked.connect(self.hide_slot)
        self.pushButton_8.clicked.connect(self.clear_fold_slot)

        self.model = QStandardItemModel()
        self.model.setColumnCount(1)
        self.model_file_paths = set()
        self.model_child_items = []
        self.model_file_path_values = dict()

        self.treeView.setIconSize(QSize(20, 20))
        self.treeView.setItemDelegate(self.TreeViewItemDelegate())
        self.treeView.setModel(self.model)
        self.treeView.setHeaderHidden(True)
        self.treeView.setStyleSheet('QTreeView{show-decoration-selected: 1;border:1px solid lightgray}'
                                    """
                                    QTreeView:focus{outline:none;color:black}
                                    QTreeView::item:hover, QTreeView::branch:hover {
                                           background-color: #CCE8FF;color:black
                                    }
                                    QTreeView::item:selected, QTreeView::branch:selected {
                                           background-color: #CCE8FF;color:black
                                    }
                                    QTreeView::item:selected:!active, QTreeView::branch:selected:!active {
                                           background-color: #CCE8FF;color:black
                                    }                                    
                                    """)
        self.treeView.clicked.connect(_tree_clicked)

        signal_manager.add_event('api_server_title', None, _set_title)
        signal_manager.add_event('api_server_add_request', None, self.add_request)
        signal_manager.add_event('api_server_update_request', None, self.update_request)

    def update_request(self):
        for index in range(self.model.rowCount()):
            root_item = self.model.item(index)
            for child_index in range(root_item.rowCount()):
                QApplication.processEvents()
                child_item = root_item.child(child_index)
                file_path, request, url_value = child_item.data(Qt.UserRole)
                if request.status == 200:
                    child_item.setIcon(QIcon(':/icon/成功.svg'))
                elif request.status != -1:
                    child_item.setIcon(QIcon(':/icon/感叹号.svg'))

    def add_request(self, file_path: str, url_value: int, request: Request):
        print('add request ', file_path, url_value, request)
        if file_path not in self.model_file_paths:
            self.model_file_paths.add(file_path)
            path = Path(file_path)
            root_item = QStandardItem()
            root_item.setText(path.name)
            root_item.setData(file_path, Qt.UserRole + 1)
            root_item.setEditable(False)
            flag = True
        else:
            for i in range(self.model.rowCount()):
                item = self.model.item(i)
                if item.data(Qt.UserRole + 1) == file_path:
                    break
            root_item = item
            flag = False
        root_item.setIcon(QIcon(':/icon/API管理.svg'))
        values = self.model_file_path_values.setdefault(file_path, set())
        if url_value not in values:
            values.add(url_value)
            child = QStandardItem(f'#{url_value}')
            child.setData([file_path, request, url_value], Qt.UserRole)
            child.setEditable(False)
            root_item.appendRow(child)
            self.model_child_items.append(child)
            self.treeView.setCurrentIndex(child.index())
        else:
            for i in range(root_item.rowCount()):
                child_item = root_item.child(i)
                if child_item.text() == f'#{url_value}':
                    # file_path, request, url_value = child_item.data(Qt.UserRole)
                    child_item.setData([file_path, request, url_value], Qt.UserRole)
                    self.treeView.setCurrentIndex(child_item.index())
                    self.model_child_items.append(child_item)
                    break
        if flag:
            self.model.appendRow(root_item)
        self.treeView.expand(root_item.index())

    def wrap_slot(self, checked):
        code = self.textBrowser.code
        if checked:
            code.setWrapMode(code.SC_WRAP_CHAR)
        else:
            code.setWrapMode(code.SC_WRAP_NONE)

    def hide_slot(self):
        self.get_app().hide_bottom_panel(1)

    def clear_fold_slot(self, checked):
        code = self.textBrowser.code
        if checked:
            code.clearFolds()
        else:
            code.foldAll()
