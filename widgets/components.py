from enum import IntEnum
from pathlib import Path
from types import MethodType
from typing import List

from PyQt5.QtCore import QSize, QFileInfo
from PyQt5.QtCore import Qt, QModelIndex, QRect, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, \
    QDropEvent, QDragMoveEvent, QCursor, QFont
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QMenu, QTabWidget, QFileSystemModel, QComboBox, QListWidget, QListWidgetItem, QCheckBox, \
    QLineEdit
from PyQt5.QtWidgets import QTreeView, QApplication, QStyledItemDelegate, QStyle, QHeaderView, QWidget, QHBoxLayout, \
    QPushButton, QFrame, QSpacerItem, QSizePolicy

from widgets.ide_sources_rc import *

# from widgets.base_lex import Themes, Lexers

undefined = object()
dark_menu_style = '''
                QMenu{background: #333231;border:1px solid #434241}
                QMenu::item{
                  padding:3px 20px;
                  color:lightgray;
                  font-size:9pt;
                  font-family:微软雅黑}
                QMenu::item:hover{
                  background-color:#242220;
                }
                QMenu::item:selected{
                  background-color:#242220;
                }'''


class MenuFlags(IntEnum):
    create_py = 0
    create_json = 1
    create_txt = 2
    create_html = 3
    create_css = 4
    create_dir = 5

    delete_file = 10
    delete_dir = 11


class DragTreeView(QTreeView):
    drop_signal = pyqtSignal(str)
    menu_signal = pyqtSignal(object, MenuFlags)

    def __init__(self, parent=None, ide=None):
        super().__init__(parent)
        self.ide = ide
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu_policy)
        self.menu_signal.connect(self._menu_slot)

    def _create_dft_file_name(self, index: QModelIndex, flag: MenuFlags):
        def _create(p: Path) -> str:
            list_files = list(p.iterdir())
            length = len(list_files)
            if flag.name.startswith('create'):
                file_name = f'新建_{flag.name.split("_")[-1]}_{length + 1}'
                return p.joinpath(file_name).__str__()
            else:
                return ''

        if index:
            value = self.model().filePath(index)
            path = Path(value)
            if path.is_file():
                return _create(path.parent)
            elif path.is_dir():
                return _create(path)
            return None

    def _delte_file_or_dir(self, index: QModelIndex, flag: MenuFlags):
        if index:
            value = self.model().filePath(index)
            path = Path(value)
            if flag == MenuFlags.delete_file:
                try:
                    path.unlink()
                except:
                    pass
            elif flag == MenuFlags.delete_dir:
                try:
                    import shutil
                    shutil.rmtree(path.__str__())
                except:
                    import traceback
                    traceback.print_exc()

    def _menu_slot(self, index, flag: MenuFlags):
        raw = self._create_dft_file_name(index, flag)
        file = raw + '.' + flag.name.split('_')[-1] if raw else None
        tab_name = Path(file).name if file else None
        if flag == MenuFlags.create_py:
            self.ide.add_python(tab_name=tab_name, created=file)
        elif flag == MenuFlags.create_txt:
            self.ide.add_text(tab_name=tab_name, created=file)

        elif flag == MenuFlags.delete_file:
            self._delte_file_or_dir(index, flag)
        elif flag == MenuFlags.delete_dir:
            self._delte_file_or_dir(index, flag)
        elif flag == MenuFlags.create_dir:
            if raw:
                path_raw = Path(raw)
                path_raw.mkdir(parents=True)

    def _menu_policy(self, pos):
        flags = MenuFlags
        menu = QMenu()
        # if self.ide._current_theme == Themes.dark:
        #     style = dark_menu_style
        # else:
        #     style = ''
        style = dark_menu_style
        menu.setStyleSheet(style)
        actions = []
        a1 = menu.addAction('新建 python 文件')
        a2 = menu.addAction('新建 json 文件')
        a3 = menu.addAction('新建 txt 文件')
        a4 = menu.addAction('新建 css 文件')
        a5 = menu.addAction('新建 html 文件')
        menu.addSeparator()
        a9 = menu.addAction('新建文件夹')
        menu.addSeparator()
        a6 = menu.addAction('删除文件')
        a7 = menu.addAction('删除文件夹')

        actions.extend(
            [(a1, flags.create_py), (a2, flags.create_json), (a3, flags.create_txt), (a4, flags.create_css),
             (a9, flags.create_dir), (a5, flags.create_html), (a6, flags.delete_file), (a7, flags.delete_dir)])
        act = menu.exec_(QCursor.pos())
        for action, flag in actions:
            if act == action:
                index = self.currentIndex()
                self.menu_signal.emit(index, flag)
                break

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        text = e.mimeData().text()
        file_info = QFileInfo(text.strip('file:///'))
        if e.mimeData().hasText() and file_info.isDir():
            e.setDropAction(Qt.MoveAction)
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        super(DragTreeView, self).dragMoveEvent(event)
        text = event.mimeData().text() or ''
        file_info = QFileInfo(text.strip('file:///'))
        if file_info.isDir():
            event.setAccepted(True)
            event.setDropAction(Qt.MoveAction)

    def dropEvent(self, e: 'QDropEvent') -> None:
        dir_path = e.mimeData().text().replace('file:///', '', -1)
        self.drop_signal.emit(dir_path)


class FileSystemModel(QFileSystemModel):
    def __init__(self, path: str):
        super(FileSystemModel, self).__init__()
        self.work_path = Path(path)

    def columnCount(self, parent: 'QModelIndex' = ...) -> int:
        return 1

    def headerData(self, section: int, orientation: 'Orientation', role=None):
        if section == 0 and role == Qt.DisplayRole:
            # f = Path(self.run_data.current_dir) if self.run_data.current_dir else None
            # if f:
            #     return f.name or '未知'
            return self.work_path.name or '未知'
            # return '未知'
        return super().headerData(section, orientation, role)

    def data(self, index: 'QModelIndex', role: int = Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DecorationRole:
                is_dir = self.isDir(index)
                file_type = self.type(index)
                if is_dir:
                    return QIcon(':/icon/文件夹.svg')
                if file_type in ['txt File', 'File']:
                    return QIcon(':/icon/txt.svg')
                elif file_type in ['py File', 'pyw File']:
                    return QIcon(':/icon/python-misc.svg')
                elif file_type in ['json File']:
                    return QIcon(':/icon/json.svg')
                elif file_type in ['js File']:
                    return QIcon(':/icon/txt.svg')
                elif file_type in ['css File']:
                    return QIcon(':/icon/css.svg')
                elif file_type in ['ui File']:
                    return QIcon(':/icon/file-xml.svg')
                elif file_type in ['http File']:
                    return QIcon(':/icon/HTTP.svg')
                elif file_type in ['html File']:
                    return QIcon(':/icon/html.svg')

            return super(FileSystemModel, self).data(index, role)
        return super(FileSystemModel, self).data(index, role)


class CodeTabFlags(IntEnum):
    fix_tab = 0
    close_tab = 1
    close_all_tab = 2
    close_all_tab_except_fixed = 3
    close_tab_except_self = 4

    run_tab = 10


class CodeTabWidget(QTabWidget):
    tab_signal = pyqtSignal(int, CodeTabFlags)
    run_signal = pyqtSignal(QWidget)

    def __init__(self, parent=None, ide=None):
        super(CodeTabWidget, self).__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._tab_menu)
        self.ide = ide
        self.tab_signal.connect(self._tab_slot)
        # self.run_signal.connect(lambda w: w._run())

    def _get_tabs_files(self) -> List[str]:
        ret = []
        for tab in range(self.count()):
            ret.append(self.widget(tab).raw_file)
        return ret

    def _get_tab_index_from_file_path(self, file_path: str) -> int:
        tabs = self._get_tabs_files()
        try:
            index = tabs.index(file_path)
            if index > -1:
                return index
            return -1
        except ValueError:
            return -1

    def _tab_slot(self, current_index: int, flag: CodeTabFlags):
        if flag == CodeTabFlags.fix_tab:
            # 固定选项卡
            self._fix_tab_widget(current_index)
        elif flag == CodeTabFlags.close_all_tab:
            # 移除所有选项卡
            removed = []
            for index in range(self.count()):
                widget = self.widget(index)
                removed.append(widget)
            for widget in removed:
                index = self.indexOf(widget)
                self.removeTab(index)
        elif flag == CodeTabFlags.close_tab_except_self:
            # 移除其他所有选项卡
            removed = []
            current_widget = self.widget(current_index)
            for index in range(self.count()):
                widget = self.widget(index)
                if getattr(widget, '_tab_fixed', None) is None:
                    removed.append(widget)
            for widget in removed:
                if widget != current_widget:
                    ind = self.indexOf(widget)
                    self.removeTab(ind)
        elif flag == CodeTabFlags.close_all_tab_except_fixed:
            # 移除未固定的选项卡
            removed = []
            for index in range(self.count()):
                widget = self.widget(index)
                if getattr(widget, '_tab_fixed', None) is None:
                    removed.append(widget)
            for widget in removed:
                index = self.indexOf(widget)
                self.removeTab(index)

    def _tab_menu(self, pos):
        index = self.tabBar().tabAt(pos)
        style = dark_menu_style
        if index >= 0:
            flags = CodeTabFlags
            menu = QMenu()
            menu.setStyleSheet(style)
            actions = []
            a1 = menu.addAction('固定选项卡')
            a2 = menu.addAction('关闭所有选项卡')
            a3 = menu.addAction('关闭其他选项卡')
            a4 = menu.addAction('关闭所有未固定选项卡')
            current = self.widget(index)

            if current.type == 'python':  # Lexers.python:
                menu.addSeparator()
                tab_name = self.tabText(index)
                icon = QIcon(QPixmap(':/icon/运行，调试.svg').scaled(15, 15, transformMode=Qt.SmoothTransformation))
                a5 = menu.addAction(icon, f'运行 {tab_name}')
                menu.setFixedWidth(menu.fontMetrics().width('关闭所有未固定选项卡') * 1.5)
            else:
                a5 = undefined

            if a5 == undefined:
                menu.addSeparator()
            sub_menu = menu.addMenu('打开于')
            a6 = sub_menu.addAction('Explorer')
            menu.addSeparator()
            a7 = menu.addAction('重命名文件')

            act = menu.exec_(QCursor.pos())
            actions.extend([(a1, flags.fix_tab), (a2, flags.close_all_tab), (a3, flags.close_tab_except_self),
                            (a4, flags.close_all_tab_except_fixed), (a5, undefined)])
            for action, flag in actions:
                if flag != undefined:
                    if action == act:
                        self.tab_signal.emit(index, flag)
                else:
                    if action == act:
                        self.run_signal.emit(current)

    def _fix_tab_widget(self, tab_index: int):
        widget = self.widget(tab_index)
        widget._tab_fixed = True
        if widget:
            icon = QIcon(':/icon/固定,图钉.svg')
            self.tabBar().setIconSize(QSize(15, 15))
            self.tabBar().setTabIcon(tab_index, icon)
            self.tabBar().moveTab(tab_index, 0)

    def addTab(self, widget: QWidget, icon: QIcon, a1: str) -> int:
        count = self.count()
        super().addTab(widget, icon, a1)
        # if widget.raw_file:
        #     self.setTabToolTip(count, widget.raw_file)


FileNameFlag = Qt.DisplayRole
RootUriFlag = Qt.UserRole
FileUriFlag = Qt.UserRole + 1
DirFlag = Qt.UserRole + 2
ModifyFlag = Qt.UserRole + 3
RootItemFlag = Qt.UserRole + 4


class VirtualFileSystemTreeView(QTreeView):
    class _TreeViewDelegate(QStyledItemDelegate):
        def paint(self, painter: QPainter, option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
            data = index.data(Qt.UserRole)
            if option.state & QStyle.State_HasFocus and data is None:
                option.font.setBold(True)
            super().paint(painter, option, index)

    class _HorizonHeaderView(QHeaderView):
        search_signal = pyqtSignal(str)
        text_signal = pyqtSignal(str)

        def __init__(self, parent=None):
            super().__init__(Qt.Horizontal, parent)
            self.header_title = QPushButton()
            self.header_title.setStyleSheet('QPushButton{background: none;border:none;font-family:微软雅黑}')
            self.header_widget = self.create_head_widget()

        def create_head_widget(self):
            def add_item(this, content: str, icon: str, tooltip=''):
                btn = QPushButton(content)
                btn.setIcon(QIcon(icon))
                btn.setStyleSheet('QPushButton{background:none;border:none;padding:0px}QPushButton:hover{'
                                  'background: lightgray;}')
                btn.setToolTip(tooltip)
                size = 24
                btn.setFixedHeight(size)
                btn.setFixedWidth(size)
                btn.setIconSize(QSize(20, 20))
                count = lay.count()
                lay.insertWidget(count, btn)
                return btn

            frame = QFrame(self)
            frame.setObjectName('HeaderFrame')
            frame.setFrameStyle(QFrame.NoFrame)
            frame.setStyleSheet('QFrame{background: #F4F4F4}')
            lay = QHBoxLayout(frame)
            lay.setSpacing(2)
            lay.setContentsMargins(5, 0, 2, 0)
            lay.addWidget(self.header_title)
            lay.addSpacerItem(QSpacerItem(20, 10, hPolicy=QSizePolicy.Expanding))
            frame.add_item = MethodType(add_item, frame)
            return frame

        def paintSection(self, painter: QPainter, rect: QRect, logicalIndex: int) -> None:
            super().paintSection(painter, rect, logicalIndex)
            self.header_widget.setGeometry(rect)

    def __init__(self):
        super(VirtualFileSystemTreeView, self).__init__()
        self.clicked.connect(self.click_slot)
        self.doubleClicked.connect(self.double_click_slot)
        self.setItemDelegate(self._TreeViewDelegate())
        self.__model = QStandardItemModel()
        self.setModel(self.__model)
        self.__header = self._HorizonHeaderView(self)
        self.setHeader(self.__header)
        self.__header.setStretchLastSection(True)
        self.__header.setFixedHeight(36)

    def click_slot(self, index: QModelIndex):
        print('clicked', index.data(Qt.DisplayRole), index.data(Qt.UserRole))

    def double_click_slot(self, index: QModelIndex):
        pass

    def clear_model(self):
        self.model().clear()

    def add_api_root(self, base_url: str, name, item: QStandardItem = None):
        """
        item:
        Qt.UserRole+1 url_path
        Qt.UserRole+2 root_flag
        Qt.UserRole+3 datetime
        """
        if item is None:
            item = QStandardItem()
        item.setText(name)
        item.setData(base_url, RootUriFlag)
        item.setData(True, DirFlag)
        item.setData(True, RootItemFlag)
        item.setToolTip(base_url)
        self.__model.appendRow(item)
        return item

    def load_dir_to_root(self, root_item: QStandardItem, data: dict, base_url: str):
        self._process_model_data2(root_item, data, base_url=base_url)
        path_root_item = root_item.takeChild(0, 0)
        path_root_item.setText(root_item.text())
        path_root_item.setToolTip(base_url)
        path_root_item.setData(base_url, RootUriFlag)
        path_root_item.setData(True, DirFlag)
        path_root_item.setData(True, RootItemFlag)

        self.__model.appendRow(path_root_item)
        row_count = self.__model.rowCount()
        self.__model.takeRow(row_count - 2)

    def add_dir_root(self, name: str, data: dict, base_url: str):
        item = QStandardItem()
        item.setText(name)
        self._process_model_data2(item, data, base_url=base_url)
        out = item.takeChild(0, 0)
        out.setText(name)
        out.setToolTip(base_url)
        out.setData(base_url, RootUriFlag)
        out.setData(True, DirFlag)
        self.__model.appendRow(out)
        return out

    def setHorizontalHeaderLabels(self, data):
        self.__model.setHorizontalHeaderLabels([''])
        self.__header.header_title.setText(data)

    def header_widget(self):
        return self.__header.header_widget

    def icon_provider(self, file_name: str, is_dir=False):
        file_type = file_name.split('.')[-1]
        if is_dir:
            return QIcon(':/icon/文件夹.svg')
        if is_dir:
            return QIcon(':/icon/文件夹.svg')
        if file_type in ['txt', '']:
            return QIcon(':/icon/txt.svg')
        elif file_type in ['py', 'pyw']:
            return QIcon(':/icon/python-misc.svg')
        elif file_type in ['json']:
            return QIcon(':/icon/json.svg')
        elif file_type in ['js']:
            return QIcon(':/icon/txt.svg')
        elif file_type in ['css']:
            return QIcon(':/icon/css.svg')
        elif file_type in ['ui']:
            return QIcon(':/icon/file-xml.svg')
        elif file_type in ['http']:
            return QIcon(':/icon/HTTP.svg')
        elif file_type in ['html']:
            return QIcon(':/icon/html.svg')
        return QIcon('')

    def add_header_item(self, content: str, icon: str, tool_tip: str) -> QPushButton:
        return self.__header.header_widget.add_item(content, icon, tool_tip)

    def _model_data_test2(self, current: Path) -> dict:
        dirs = list(current.iterdir())
        root = {}
        top_path = current.__str__()
        dirs.sort(key=lambda e: 0 if e.is_dir() else 1)
        for d in dirs:
            if d.is_file():
                v = root.setdefault(top_path, [])
                v.append(d.__str__())
            else:
                v = root.setdefault(top_path, [])
                v.append(self._model_data_test2(d))
        if not dirs:
            root.setdefault(top_path, [])

        return root

    def _process_model_data2(self, model: QStandardItem, data: dict, parent_item: QStandardItem = None,
                             base_url: str = None):
        """
           item:
               Qt.UserRole   http_path file_item
               Qt.UserRole+1 is_dir bool
               # Qt.UserRole+2 dir_flag
           """
        for d, v in data.items():
            dir_name = d.split('\\')[-1]
            dir_item = QStandardItem(dir_name)
            dir_item.setData(f'{base_url}', FileUriFlag)
            dir_item.setData(True, DirFlag)
            dir_item.setIcon(self.icon_provider('', True))
            dir_item.setEditable(False)
            if parent_item is None:
                model.appendRow(dir_item)
            else:
                parent_item.appendRow(dir_item)
            for value in v:
                if isinstance(value, dict):
                    self._process_model_data2(model, value, dir_item, base_url)
                else:
                    file_name = value.split('\\')[-1]
                    file_uri = base_url + value.replace('\\', '/')
                    file_item = QStandardItem()
                    file_item.setText(file_name)
                    file_item.setData(file_uri, FileUriFlag)
                    file_item.setData(False, DirFlag)
                    file_item.setIcon(self.icon_provider(file_name, False))
                    file_item.setEditable(False)
                    dir_item.appendRow(file_item)
        return model


class MultiSelectComboBox(QComboBox):
    def __init__(self, *a, **kw):
        super(MultiSelectComboBox, self).__init__(*a, **kw)
        self.line = QLineEdit()
        self.checkAll = QCheckBox()
        self.checkAll.setText('全选')
        self.checkAll.clicked.connect(self.check_all_clicked)

        self.list_widget = QListWidget()

        item = QListWidgetItem()
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, self.checkAll)
        self.setModel(self.list_widget.model())
        self.setView(self.list_widget)
        self.setLineEdit(self.line)
        self.line.setStyleSheet('QLineEdit{font-family:微软雅黑; color:red;border:none}')
        self.line.setText('输出内容')
        self.line.setReadOnly(True)

    def check_all_clicked(self, checked: bool):
        for i in range(self.list_widget.count()):
            if i != 0:
                item = self.list_widget.item(i)
                checked_box = self.list_widget.itemWidget(item)
                checked_box.setChecked(checked)

    def add_item(self, text, state=False):
        item = QListWidgetItem()
        self.list_widget.addItem(item)
        checked = QCheckBox()
        checked.setText(text)
        checked.setChecked(state)
        checked.setFont(QFont('微软雅黑'))
        self.list_widget.setItemWidget(item, checked)


if __name__ == '__main__':
    app = QApplication([])
    root_path = Path(__file__).parent
    view = VirtualFileSystemTreeView()
    model_data = view._model_data_test(root_path)
    item = view.add_api_root('192.168.0.1', 'aaaa')
    view.load_dir_to_root(item, model_data)
    view.setHorizontalHeaderLabels('gggg')
    view.header().resizeSection(0, 160)
    view.add_header_item('fuck', '')
    view.add_header_item('222', '')

    # 设置成有虚线连接的方式
    # view.setStyle(QStyleFactory.create('windows'))
    # 完全展开
    view.expandAll()

    view.show()

    app.exec_()
