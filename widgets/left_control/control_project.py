from pathlib import Path

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QSpacerItem, QSizePolicy, QTreeView)

from pyqt5utils.components.styles import StylesHelper
from widgets.base import PluginBaseMixIn
from . import register
from ..components import FileSystemModel
from ..factorys import styled_factory
from ..signals import signal_manager
from ..styles import current_styles

WorkPathFlag = Qt.UserRole + 10


@register('项目', index=0, icon=':/icon/24gf-folderOpen.svg')
class ProjectTreeViewWidget(QWidget, PluginBaseMixIn, styled_factory('background-darker')):
    model: FileSystemModel = None  # type hint

    def __init__(self):
        super(ProjectTreeViewWidget, self).__init__()
        lay = QVBoxLayout()
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        self.init_panel(lay)
        self.init_signals()
        self.setLayout(lay)

    def render_custom_style(self):
        border_color = current_styles.border
        background = current_styles.background_lighter
        handler_color = current_styles.handler
        color = current_styles.foreground
        self.project_view.header().setStyleSheet('QHeaderView:section{background:%s;color:%s;border:none}' % (background, color))
        self.project_view.setStyleSheet('QTreeView{border:1px solid %s;background:%s;color: %s}' % (border_color, background, color))
        StylesHelper.set_v_history_style_dynamic(self.project_view, color=handler_color, background='transparent')
        StylesHelper.set_v_history_style_dynamic(self.project_view, color=handler_color, background='transparent')

    def _open_file(self, index: QModelIndex):
        # file_type = self.model.type(index)
        # file_name = self.model.fileName(index)
        file_path = self.model.filePath(index)
        signal_manager.emit(signal_manager.openProjectFile, file_path)

    def init_panel(self, lay: QVBoxLayout):
        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame_lay = QHBoxLayout(frame)
        frame_lay.setContentsMargins(0, 0, 0, 0)
        label = QLabel()
        label.setText('资源管理')
        label.setFont(QFont('微软雅黑'))
        label.setIndent(4)
        frame_lay.addWidget(label)
        frame_lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))

        lay.addWidget(frame)
        self.project_view = QTreeView()
        self.project_view.doubleClicked.connect(self._open_file)
        self.project_view.setStyleSheet('QTreeView{border:none}')

        lay.addWidget(self.project_view)

    def load_project(self, path: str):
        if self.model is None:
            self.model = FileSystemModel(path)
            self.project_view.setModel(self.model)
        self.model.setRootPath(path)
        self.project_view.setRootIndex(self.model.index(path))
        self.get_app().r_run_time.current = Path(path)
        self.model.work_path = Path(path)

    def init_signals(self):
        signal_manager.add_event(signal_manager.loadProject, None, call_back=self.load_project)

    ###
    def when_app_exit(self, main_app):
        current_path: Path = self.get_app().r_run_time.current
        config_name = self.config_name('project')
        if current_path:
            self.settings.setValue(config_name, current_path.__str__())

    def when_app_start_up(self, main_app):
        config_name = self.config_name('project')
        project_path = self.settings.value(config_name)
        if project_path is not None:
            self.load_project(project_path)
