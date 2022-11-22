import sys
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QButtonGroup, QAction, QWidget, qApp
from jedi.api.environment import SameEnvironment
from pydantic import BaseModel, Field

from pyqt5utils.components import Message
from ui.main2ui import Ui_MainWindow
from widgets.base import PluginBaseMixIn
from widgets.collect import collect_plugins, Collections
from widgets.components import FileSystemModel
from widgets.factorys import add_styled
from widgets.interfaces import ITabInterFace
from widgets.signals import app_exit, app_start_up
from widgets.utils import ConfigProvider, ConfigKey, IconProvider


class AppRunTime(BaseModel):
    current: Path = Field(None, description='当前工作目录')
    read_only: bool = Field(False, description='阅读模式')


class MainWidget(QMainWindow, Ui_MainWindow, PluginBaseMixIn):
    model: FileSystemModel = None
    plugins: Collections  # type hint
    single_step = ConfigProvider.default(ConfigKey.general, 'single_step')
    app_name = 'FEditor'

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

    def render_style_sheet(self):
        self.tabWidget.setFont(QFont('微软雅黑'))
        # self.tabWidget_2.setFont(QFont('微软雅黑'))

    def init_run_time(self):
        self.r_run_time: AppRunTime = AppRunTime()

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

        self.toolbar.setIconSize(QSize(20, 20))

    def load_status(self):
        cl = sorted(self.plugins.status, key=lambda k: self.plugins.status[k]['index'])
        for clz in cl:
            widget = clz()
            self.statusbar.addPermanentWidget(widget)

    def after_init(self):
        self.set_provider('main_app', self)
        app_start_up.send(self)

    def init_signal_manager(self):
        def _change_h_split_size(size1, size2):
            self.splitter.setSizes([size1, size2])

        def _change_v_split_size(size1, size2):
            self.splitter_2.setSizes([size1, size2])

        def _change_read_state(v):
            self.r_run_time.read_only = v

        def _show_message(msg: str, timeout: int = 0):
            self.statusbar.showMessage(msg, timeout)

        def _create_file(file_path: str, file_content: str):
            # path = self.r_run_time.current / file_path
            path = Path(file_path)
            path.write_text(file_content, encoding='utf-8')

        def _create_file_and_open(file_path: str, file_content: str):
            path = Path(file_path)
            if not path.exists():
                path.touch()
                path.write_text(file_content, encoding='utf-8')
            self.open_file(file_path)
            # file_type, file_name = get_file_type_and_name(file_path)
            # self.add_tab_widget(file_type, file_name, file_path)

        def _create_hook_file_and_open(file_path: str, file_content: str):
            path = Path(file_path)
            if not path.exists():
                path.touch()
                path.write_text(file_content, encoding='utf-8')
            self.open_file(file_path)
            # file_type, file_name = get_file_type_and_name(file_path)
            # self.add_tab_widget(file_type, file_name, file_path)

        def _open_project_file(file_path):
            self.open_file(file_path)

        def _open_file_and_move(file_path, line=None, col=None):
            self.open_file(file_path, line, col)

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
        signal_manager.add_event(signal_manager.statusReadOnly, None, call_back=_change_read_state)
        signal_manager.add_event(signal_manager.statusMsg, None, call_back=_show_message)
        signal_manager.add_event(signal_manager.createFile, None, call_back=_create_file)
        signal_manager.add_event(signal_manager.createFileAndOpen, None, call_back=_create_file_and_open)
        signal_manager.add_event(signal_manager.createHookFileAndOpen, None, call_back=_create_hook_file_and_open)
        signal_manager.add_event(signal_manager.openProjectFile, None, call_back=_open_project_file)
        signal_manager.add_event(signal_manager.openFileAndMoveCursor, None, call_back=_open_file_and_move)
        self.sm = signal_manager

    def init_project(self):

        def remove_tab(index):
            self.tabWidget.removeTab(index)

        self.tabWidget.tabCloseRequested.connect(remove_tab)

        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([200, 500])

        self.setWindowTitle(self.app_name)
        self.setWindowIcon(QIcon(r'D:\work\httpfile\sources\编辑.svg'))

        # style
        add_styled(self.tabWidget, 'tab')
        add_styled(self, 'background-darker')
        add_styled(self.statusbar, 'status-bar')
        add_styled(qApp, 'qApp')

    def load_left(self):
        self.left_buttons = QButtonGroup()

        def _splitter_moved(pos, handle_index):
            if handle_index == 1:
                current = self.splitter.widget(0).currentWidget()
                if not current.isVisible():
                    current.show()

        def switch_to(target: QWidget, index):
            if target.isVisible():
                target.hide()
                self.splitter.setSizes([0, 1000])
            else:
                target.show()
                sizes = self.splitter.sizes()
                if sizes[0] <= 0:
                    sizes = [200, 1000]
                self.splitter.setSizes(sizes)
            self.stackedWidget.setCurrentWidget(target)

        add_styled(self.splitter, 'splitter')
        add_styled(self.splitter_2, 'splitter')
        add_styled(self.splitter_3, 'splitter')

        left_checked = self.config_name('left_checked')
        checked_index = self.settings.value(left_checked)
        if checked_index is None:
            checked_index = 0
        self.splitter.splitterMoved.connect(_splitter_moved)
        cl = sorted(self.plugins.left_controls, key=lambda k_clz: self.plugins.left_controls[k_clz]['index'])
        for i, k in enumerate(cl):
            v = self.plugins.left_controls[k]
            name = v['name']
            btn = QPushButton()
            btn.setIcon(QIcon(v['icon'] or ''))
            btn.setToolTip(name)
            btn.setIconSize(QSize(20, 20))
            btn.setCheckable(True)
            btn.index = i
            add_styled(btn, 'left-button')
            widget = k()
            self.stackedWidget.addWidget(widget)
            count = self.verticalLayout.count()
            self.verticalLayout.insertWidget(count - 1, btn)
            btn.clicked.connect(lambda checked, target=widget, index=i: switch_to(target, index))
            self.left_buttons.addButton(btn, i)
        self.left_buttons.button(checked_index).click()

    def load_right(self):
        pass

    def load_bottom(self):
        def _bottom_clicked():
            sender = self.sender()
            current = self.stackedWidget_3.currentWidget()
            plugin: QWidget = sender._bind_bottom
            if current != plugin:
                self.stackedWidget_3.hide()
            self.stackedWidget_3.setCurrentWidget(plugin)
            if self.stackedWidget_3.isHidden():
                self.stackedWidget_3.show()
            else:
                self.stackedWidget_3.hide()

        self.bottom_groups = QButtonGroup()
        i = 0
        cl = sorted(self.plugins.controls, key=lambda k: self.plugins.controls[k]['index'])
        for k in cl:
            i += 1
            v = self.plugins.controls[k]
            name, icon = v['name'], v['icon']
            btn = QPushButton()
            btn.setCheckable(True)
            add_styled(btn, 'bottom-button')
            btn.setText(name)
            if icon:
                btn.setIcon(QIcon(icon))
            length = self.horizontalLayout_2.count()
            self.horizontalLayout_2.insertWidget(length - 1, btn)
            plugin_widget = k()
            plugin_widget.bottom_btn = btn
            plugin_widget.bottom_btn.clicked.connect(plugin_widget.bottom_clicked_slot)
            plugin_widget.check_state_signal.connect(plugin_widget.check_state_signal_slot)
            btn._bind_bottom = plugin_widget
            btn.clicked.connect(_bottom_clicked)
            self.stackedWidget_3.addWidget(plugin_widget)

            self.bottom_groups.addButton(btn, i - 1)

        self.stackedWidget_3.hide()

    def show_bottom_panel(self, index: int):
        btn = self.bottom_groups.button(index)
        widget = self.stackedWidget_3.widget(index)
        if widget.isHidden():
            btn.click()

    def hide_bottom_panel(self, index: int):
        btn = self.bottom_groups.button(index)
        widget = self.stackedWidget_3.widget(index)
        if not widget.isHidden():
            btn.click()

    def load_dir_path(self, path: str):
        pass

    #### add tab ####
    def add_tab_widget(self, file_type, file_name, file_path: str, url: str = None, content: str = None):
        icon = IconProvider.get_icon(file_name)
        if url is None:
            def _create_tab_code_widget():
                for k, v in self.plugins.tabs.items():
                    # print('imp by: ', ITabInterFace.implementedBy(k))
                    if file_type in v:
                        code = k()
                        code.is_remote = False
                        code.load_file(file_path)
                        return code

            tab: ITabInterFace = _create_tab_code_widget()
            if tab:
                tab.set_read_only(self.r_run_time.read_only)
                self.tabWidget.addTab(tab, icon, file_name)
                self.tabWidget.setCurrentWidget(tab)
            return tab
        else:
            file_type = url.split('.')[-1] + ' File'

            def _create_tab_code_widget():
                for k, v in self.plugins.tabs.items():
                    if file_type in v:
                        code = k()
                        code.is_remote = True
                        code.load_file(url, content)
                        return code

            tab: ITabInterFace = _create_tab_code_widget()
            if tab:
                tab.set_read_only(self.r_run_time.read_only)
                self.tabWidget.addTab(tab, icon, url)
                self.tabWidget.setCurrentWidget(tab)
            return tab

    def open_file(self, file_path: str, line: int = None, col: int = None):
        path = Path(file_path)
        file_name = path.name
        file_type = path.suffix.replace('.', '', 1) + ' File'
        # print('open file ', file_path, file_name, file_type)
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if widget.file_path() == file_path:
                self.tabWidget.setCurrentWidget(widget)
                if line is not None and col is not None:
                    widget.move_to(line, col)
                return
        tab = self.add_tab_widget(file_type, file_name, file_path)
        if tab:
            if line is not None and col is not None:
                tab.move_to(line, col)

    ### close
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
        left_checked = self.config_name('left_checked')
        w, h = self.width(), self.height()
        self.settings.setValue(key, [pos.x(), pos.y()])
        self.settings.setValue(size_key, [w, h])
        checked_index = self.left_buttons.checkedButton().index
        self.settings.setValue(left_checked, checked_index)

    ### interface
    def current_file_path(self) -> Optional[str]:
        widget = self.tabWidget.currentWidget()
        if widget:
            return widget.file_path()

    def get_python_info(self) -> SameEnvironment:
        return self.get_provider('python_info')

    @classmethod
    def run(cls):
        plugins = collect_plugins()
        cls.plugins = plugins
        app = QApplication(sys.argv)
        mainapp = cls()
        mainapp.show()
        app.exec_()


run = MainWidget.run
