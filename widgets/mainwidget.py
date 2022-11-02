import sys
from pathlib import Path

from PyQt5.QtCore import QModelIndex, QPoint, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QButtonGroup, QAction
from pydantic import BaseModel, Field

from pyqt5utils.components import Message
from pyqt5utils.components.styles import StylesHelper
from ui.main2ui import Ui_MainWindow
from widgets.base import PluginBaseMixIn
from widgets.collect import collect_plugins, Collections
from widgets.components import FileSystemModel
from widgets.signals import app_exit, app_start_up
from widgets.utils import ConfigProvider, ConfigKey


class RunTime(BaseModel):
    current: Path = Field(None, description='当前工作目录')


class MainWidget(QMainWindow, Ui_MainWindow, PluginBaseMixIn):
    model: FileSystemModel = None
    plugins: Collections  # type hint
    single_step = ConfigProvider.default(ConfigKey.general, 'single_step')

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_run_time()
        self.init_project()
        self.load_menu_bar()
        self.load_tool_bar()
        self.load_left()
        self.load_right()
        self.load_bottom()
        self.load_status()
        self.init_signal_manager()

    def init_run_time(self):
        self.r_run_time: RunTime = RunTime()

    def load_menu_bar(self):
        pass

    def load_tool_bar(self):
        self.toolbar = self.addToolBar('File')
        cl = sorted(self.plugins.toolbar_actions, key=lambda k: self.plugins.toolbar_actions[k]['index'])
        for clz in cl:
            v = self.plugins.toolbar_actions.get(clz)
            tool_tip, icon = v.get('tool_tip'), v.get('icon')
            action_provider = clz(self)
            action: QAction = action_provider.make_action(icon, tool_tip, self)
            action.triggered.connect(lambda e, ac=action_provider: ac.action_slot())
            self.toolbar.addAction(action)

        self.toolbar.setIconSize(QSize(24, 24))

    def load_status(self):
        cl = sorted(self.plugins.status, key=lambda k: self.plugins.status[k]['index'])
        for clz in cl:
            widget = clz()
            self.statusbar.addPermanentWidget(widget)

    def after_init(self):
        self.set_provider('main_app', self)
        StylesHelper.set_v_history_style_dynamic(self.treeView, color='#CFCFCF', background='transparent', width=10)
        StylesHelper.set_h_history_style_dynamic(self.treeView, color='#CFCFCF', background='transparent', height=10)
        self.treeView.setVerticalScrollMode(self.treeView.ScrollPerPixel)
        self.treeView.verticalScrollBar().setSingleStep(self.single_step.value)
        self.treeView.setHorizontalScrollMode(self.treeView.ScrollPerPixel)
        self.treeView.horizontalScrollBar().setSingleStep(self.single_step.value)
        app_start_up.send(self)

    def init_signal_manager(self):
        def _change_h_split_size(size1, size2):
            self.splitter.setSizes([size1, size2])

        def _change_v_split_size(size1, size2):
            self.splitter_2.setSizes([size1, size2])

        from widgets.signals import signal_manager
        signal_manager.add_event(signal_manager.openUrlFile, None,
                                 call_back=lambda url, content: self.add_tab_widget(None, None, None, url,
                                                                                    content))
        signal_manager.add_event(signal_manager.changeSplitSize, None, call_back=_change_h_split_size)
        signal_manager.add_event(signal_manager.changeVSplitSize, None, call_back=_change_v_split_size)
        signal_manager.add_event(signal_manager.info, None,
                                 call_back=lambda msg, dura=1500: Message.info(msg, self, dura))
        signal_manager.add_event(signal_manager.warn, None,
                                 call_back=lambda err, dura=1500: Message.warn(f'{err}', self, dura))
        self.sm = signal_manager

    def init_project(self):
        def click_file(index: QModelIndex):
            file_type = self.model.type(index)
            file_name = self.model.fileName(index)
            file_path = self.model.filePath(index)
            self.add_tab_widget(file_type, file_name, file_path)

        def remove_tab(index):
            self.tabWidget.removeTab(index)

        self.tabWidget.tabCloseRequested.connect(remove_tab)

        work_path = Path.cwd().__str__()
        self.model = FileSystemModel(work_path)
        self.treeView.setModel(self.model)
        self.treeView.doubleClicked.connect(click_file)
        self.treeView.setStyleSheet('QTreeView{border:none}')
        self.load_dir_path(work_path)

        # self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([200, 500])

        self.tabWidget_2.setStyleSheet('QTabWidget{background:red}')

    def load_left(self):
        i = 0
        cl = sorted(self.plugins.left_controls, key=lambda k: self.plugins.left_controls[k]['index'])
        for k in cl:
            i += 1
            v = self.plugins.left_controls[k]
            name = v['name']
            self.tabWidget_2.addTab(k(), name)

    def load_right(self):
        pass

    def load_bottom(self):
        self.bottom_groups = QButtonGroup()
        i = 0
        cl = sorted(self.plugins.controls, key=lambda k: self.plugins.controls[k]['index'])
        for k in cl:
            i += 1
            v = self.plugins.controls[k]
            name, icon = v['name'], v['icon']
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setStyleSheet('QPushButton{background: transparent;border:none;padding:4px;font-family:微软雅黑}'
                              'QPushButton:hover{background: lightgray;}'
                              'QPushButton:checked{background: lightgray}')
            btn.setText(name)
            if icon:
                btn.setIcon(QIcon(icon))
            length = self.horizontalLayout_3.count()
            self.horizontalLayout_3.insertWidget(length - 1, btn)
            plugin_widget = k()
            plugin_widget.bottom_btn = btn
            plugin_widget.bottom_btn.clicked.connect(plugin_widget.bottom_clicked_slot)
            plugin_widget.check_state_signal.connect(plugin_widget.check_state_signal_slot)
            btn._bind_bottom = plugin_widget
            btn.clicked.connect(lambda e: (
                self.stackedWidget_3.show(),
                self.stackedWidget_3.setCurrentWidget(self.sender()._bind_bottom)))
            self.stackedWidget_3.addWidget(plugin_widget)

            self.bottom_groups.addButton(btn)
        self.stackedWidget_3.hide()

    def load_dir_path(self, path: str):
        self.model.setRootPath(path)
        self.treeView.setRootIndex(self.model.index(path))
        self.r_run_time.current = Path(path)
        self.model.work_path = Path(path)

    #### add tab ####
    def add_tab_widget(self, file_type, file_name, file_path: str, url: str = None, content: str = None):
        print('call add tab', file_type, file_name, file_path)
        if url is None:
            def _create_tab_code_widget():
                for k, v in self.plugins.tabs.items():
                    if file_type in v:
                        code = k()
                        code.load_file(file_path)
                        return code

            tab = _create_tab_code_widget()
            self.tabWidget.addTab(tab, file_name)
            self.tabWidget.setCurrentWidget(tab)
        else:
            file_type = url.split('.')[-1] + ' File'
            print('here', file_type, self.plugins.tabs)

            def _create_tab_code_widget():
                for k, v in self.plugins.tabs.items():
                    if file_type in v:
                        code = k()
                        code.load_content(content)
                        return code

            tab = _create_tab_code_widget()
            self.tabWidget.addTab(tab, url)
            self.tabWidget.setCurrentWidget(tab)

    ###close
    def closeEvent(self, a0) -> None:
        app_exit.send(self)
        super().closeEvent(a0)

    def when_app_start_up(self, main_app):
        key = self.config_name('point')
        pos = self.settings.value(key)
        size_key = self.config_name('size')
        size = self.settings.value(size_key)
        if pos:
            self.move(QPoint(*pos))
        if size:
            self.resize(*size)

    def when_app_exit(self, main_app):
        key = self.config_name('point')
        pos = self.pos()
        size_key = self.config_name('size')
        w, h = self.width(), self.height()
        self.settings.setValue(key, [pos.x(), pos.y()])
        self.settings.setValue(size_key, [w, h])

    @classmethod
    def run(cls):
        plugins = collect_plugins()
        cls.plugins = plugins
        app = QApplication(sys.argv)
        mainapp = cls()
        mainapp.show()
        app.exec_()


run = MainWidget.run
