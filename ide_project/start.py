# -*- coding: utf-8 -*-
# @Time    : 2022/3/4 16:25
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : run.py
# @Software: PyCharm

import sys
import pathlib
import tempfile
import subprocess

from pathlib import Path
from types import MethodType
from typing import List

from PyQt5.QtWidgets import QApplication, QWidget, QMdiSubWindow, QVBoxLayout, QFrame, QTextBrowser, QHBoxLayout, \
    QPushButton, QSpacerItem, QSizePolicy, QFileSystemModel, QButtonGroup, QTreeView, QHeaderView, QAbstractButton
from PyQt5.QtGui import QFont, QColor, QPalette, QFontMetrics, QImage, QIcon, QStandardItemModel
from PyQt5.QtCore import Qt, QProcess, QThread, pyqtSignal, QSize, QDir, QModelIndex

from ui.mainui import Ui_Form
from widgets.lex_config import LexGetter
from widgets.base_lex import Lexers, Themes, BaseCodeWidget
from qss.styles import Styles
from config import AppConfig
from models import RunData


class FileSystemModel(QFileSystemModel):

    def __init__(self, run_data: RunData):
        super(FileSystemModel, self).__init__()
        self.run_data = run_data

    def columnCount(self, parent: 'QModelIndex' = ...) -> int:
        return 1

    def headerData(self, section: int, orientation: 'Orientation', role=None):
        if section == 0 and role == Qt.DisplayRole:
            f = Path(self.run_data.current_dir) if self.run_data.current_dir else None
            if f:
                return f.name or '未知'
            return '未知'
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

            return super(FileSystemModel, self).data(index, role)
        return super(FileSystemModel, self).data(index, role)


class IDE(QWidget, Ui_Form):
    _stand_fm: QFontMetrics = None
    _current_lex: Lexers = None
    _current_theme: Themes = Themes.dark
    _tab_icons = {Lexers.python: ':/icon/python-misc.svg',
                  Lexers.text: ':/icon/txt.svg',
                  Lexers.json: ':/icon/json.svg'}
    run_data = RunData()

    @property
    def stand_height(self):
        if getattr(self, '_stand_fm', None) is None:
            self._stand_fm = QFontMetrics(QFont('微软雅黑', 10))
        return self._stand_fm.height()

    @property
    def stand_width(self):
        if getattr(self, '_stand_fm', None) is None:
            self._stand_fm = QFontMetrics(QFont('微软雅黑', 10))
        return self._stand_fm.width('微')

    def __init__(self):
        super(IDE, self).__init__()
        self.coder_class = LexGetter
        self.config = AppConfig()
        self.setupUi(self)
        self.init_project()
        self.init_lexs()
        self.init_codes()
        self.init_bottom()
        self.set_slots()
        self.set_style()
        self.after_inits()

    def init_project(self):
        def click_file(index: QModelIndex):
            file_type = self.model.type(index)
            file_name = self.model.fileName(index)
            file_path = self.model.filePath(index)
            if file_type in ['py File', 'pyw File']:
                self.add_python(file_name, file_path)
            elif file_type in ['txt File', 'File']:
                self.add_text(file_name, file_path)
            elif file_type in ['json File']:
                self.add_json(file_name, file_path)
            elif file_type in ['js File']:
                self.add_javascript(file_name, file_path)

        def left_group(btn):
            print('btn', btn)
            if btn == self.pushButton_4:
                if self.treeView.isHidden():
                    self.treeView.show()
                else:
                    self.treeView.hide()

        self.model = FileSystemModel(self.run_data)
        self.treeView.ide = self
        self.tabWidget.ide = self
        self.treeView.setModel(self.model)
        self.treeView.doubleClicked.connect(click_file)
        self.treeView.drop_signal.connect(self.load_dir)
        header: QHeaderView = self.treeView.header()
        header.hide()
        self.load_dir(QDir.currentPath())

        self.btn_group = QButtonGroup()
        self.left_group = QButtonGroup()
        self.right_group = QButtonGroup()
        self.bottom_group = QButtonGroup()

        self.left_group.addButton(self.pushButton_4)
        self.left_group.buttonClicked[QAbstractButton].connect(left_group)

    def init_lexs(self):
        self._current_lex = Lexers.python

    def init_left(self):
        pass

    def init_right(self):
        pass

    def init_codes(self):
        self.splitter.setSizes([100, 100])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.splitter_2.setSizes([300, 100])
        self.splitter_2.setStretchFactor(0, 1)
        self.splitter_2.setStretchFactor(1, 0)

    def init_bottom(self):
        scaled = 1.2
        self.frame_5.setFixedHeight(self.stand_height * scaled)
        for widget in self.frame_5.children():
            try:
                widget.setFixedHeight(self.stand_height * scaled)
            except:
                pass

        self.frame.setFixedWidth(self.stand_width * 2)
        self.frame_3.setFixedWidth(self.stand_width * 1.5)
        self.frame_4.setFixedWidth(self.stand_width * 1.5)

    def after_inits(self):
        self.add_python('test.py')

    ############### load dir ###############
    def load_dir(self, dir_path):
        self.run_data.current_dir = dir_path
        self.model.setRootPath(dir_path)
        self.treeView.setRootIndex(self.model.index(dir_path))

    ############### tab ####################

    def _get_tabs_files(self) -> List[str]:
        ret = []
        for tab in range(self.tabWidget.count()):
            ret.append(self.tabWidget.widget(tab).raw_file)
        return ret

    def _add_tab(self, type: Lexers, tab_name: str = None, file_path: str = None, created: str = None):
        def update_line(line, col):
            self.pushButton_8.setText(f'{line + 1}:{col}')

        tabs = self._get_tabs_files()

        if file_path is not None:
            try:
                tab_index = tabs.index(file_path)
                if tab_index > -1:
                    self.tabWidget.setCurrentIndex(tab_index)
                    return
            except ValueError:
                pass

        # code widget
        code_widget = self._create_code(
            self._current_theme, tab_name, type, file_path
        )
        code_widget.ide = self
        btn = self._add_tab_btn(tab_name)
        btn.clicked.connect(lambda: self.textBrowser.setText('\n'.join(code_widget.run_content)))
        code_widget._btn = btn

        # hook
        if type == Lexers.text:
            code_widget.setFont(QFont('宋体', 11))

        code_widget.cursor_signal.connect(update_line)
        self.tabWidget.addTab(code_widget, tab_name)
        count = self.tabWidget.count()
        self.tabWidget.setFont(QFont('微软雅黑'))
        self.tabWidget.setCurrentIndex(count - 1)
        tab_icon = self._tab_icons.get(type, '')
        self.tabWidget.setTabIcon(count - 1, QIcon(tab_icon))

        # create file
        if created:
            path = Path(created)
            try:
                path.touch()
                path.mkdir(parents=True)
            except:
                pass

    def add_python(self, tab_name: str = None, file_path: str = None, created=None):
        if tab_name is None:
            tab_name = f'new%s.py' % (self.tabWidget.count() + 1)
        self._add_tab(Lexers.python, tab_name, file_path, created)

    def add_text(self, tab_name: str = None, file_path: str = None, created=None):
        self._add_tab(Lexers.text, tab_name, file_path, created)

    def add_javascript(self, tab_name: str = None, file_path: str = None, created=None):
        self._add_tab(Lexers.javascript, tab_name, file_path, created)

    def add_json(self, tab_name: str = None, file_path: str = None, created=None):
        self._add_tab(Lexers.json, tab_name, file_path, created)

    def _create_code(self, theme: Themes, file_name: str, lex_type: Lexers, raw_file):
        return self.coder_class.get_lexer(theme, file_name, lex_type, self.textBrowser, raw_file, self.config)

    def _add_tab_btn(self, tab_name: str) -> QPushButton:
        btn = QPushButton()
        btn.setText(tab_name)
        btn.setCheckable(True)
        layout: QHBoxLayout = self.frame_8.layout()
        count = layout.count()
        btn.setFixedHeight(self.stand_height * 1.3)
        layout.insertWidget(count - 1, btn)
        self.frame_8.setFixedHeight(btn.height())
        style = ''
        if self._current_theme == Themes.dark:
            style = 'QPushButton{padding:3px 5px; background:#333231;color:lightgray}' \
                    'QPushButton:hover{background: #171615}' \
                    'QPushButton:checked{color: #FFB900}'
        btn.setStyleSheet(style)
        self.btn_group.addButton(btn)

        return btn

    #############  slots  ###############

    def set_slots(self):
        def run():
            widget: BaseCodeWidget = self.tabWidget.currentWidget()
            if widget:
                widget._run()

        def remove_tab(index):
            widget = self.tabWidget.widget(index)
            self.frame_8.layout().removeWidget(widget._btn)
            widget._btn.deleteLater()
            self.tabWidget.removeTab(index)

        # 执行脚本命令
        self.pushButton.clicked.connect(run)
        self.tabWidget.tabCloseRequested.connect(remove_tab)

    #############  style  ###############
    def set_style(self):
        if self._current_theme == Themes.dark:
            self.treeView.setStyleSheet('''background:#2D2B29;color:white''')
            self.setStyleSheet(Styles.dark)


if __name__ == '__main__':
    print('start ...')
    app = QApplication([])
    code = IDE()
    code.show()
    app.exec_()
