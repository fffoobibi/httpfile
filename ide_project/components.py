from typing import List

from PyQt5.QtWidgets import QApplication, QWidget, QMdiSubWindow, QVBoxLayout, QFrame, QTextBrowser, QHBoxLayout, \
    QPushButton, QSpacerItem, QSizePolicy, QFileSystemModel, QTreeView, QMenu, QTabWidget
from PyQt5.QtGui import QFont, QColor, QPalette, QFontMetrics, QImage, QIcon, QStandardItemModel, QDragEnterEvent, \
    QDropEvent, QDragMoveEvent, QCursor, QPixmap
from PyQt5.QtCore import Qt, QProcess, QThread, pyqtSignal, QSize, QDir, QModelIndex, QFileInfo

from enum import IntEnum
from pathlib import Path

from widgets.base_lex import Themes, Lexers

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
        if self.ide._current_theme == Themes.dark:
            style = dark_menu_style
        else:
            style = ''
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
        self.run_signal.connect(lambda w: w._run())

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
        if self.ide._current_theme == Themes.dark:
            style = dark_menu_style
        else:
            style = ''

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

            if current.type == Lexers.python:
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

    def addTab(self, widget: QWidget, a1: str) -> int:
        count = self.count()
        super().addTab(widget, a1)
        if widget.raw_file:
            self.setTabToolTip(count, widget.raw_file)
