import sys
import typing
from pathlib import Path
# from types import NoneType
from typing import Optional, List, Tuple

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QColor, QPalette, QFontMetrics
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QButtonGroup, QAction, QWidget, qApp, QWidgetAction
from cached_property import cached_property
from jedi.api.environment import SameEnvironment
from lsprotocol.types import ServerCapabilities
from pydantic import BaseModel, Field

from lsp.interface import LSPAppMixIn
from pyqt5utils import color_widget
from pyqt5utils.components import Message
from ui.main2ui import Ui_MainWindow
from widgets.base import PluginBaseMixIn
from widgets.collect import collect_plugins, Collections
from widgets.components import FileSystemModel
from widgets.factorys import add_styled
from widgets.fonts import DirFontLoader
from widgets.handler import handler_lsp_msg
from widgets.hooks import run_lsp_hook
from widgets.interfaces import ITabInterFace
from widgets.signals import app_exit, app_start_up
from widgets.styles import current_styles
from widgets.utils import ConfigProvider, ConfigKey, IconProvider

icon = r'D:\work\httpfile\sources\编辑.svg'
plugins = collect_plugins()


class AppRunTime(BaseModel):
    current: Path = Field(None, description='当前工作目录')
    read_only: bool = Field(False, description='阅读模式')
    font_src: List[int] = Field(default_factory=list)


@color_widget(title='FEditor', icon=icon,
              bar_color=current_styles.title_background,
              text_color=current_styles.foreground,
              back_ground_color=current_styles.background_darker,
              border_color=current_styles.border,
              button_text_color=current_styles.foreground,
              set_bkg=False)
class MainWidget(QMainWindow, Ui_MainWindow, PluginBaseMixIn, LSPAppMixIn):
    __lsp_initials__ = {}

    def lsp_current_line_col(self) -> Tuple[int]:
        tab = self.current_tab()
        if tab and tab.support_code:
            return tab.code.current_line_col

    def create_lsp_hook_func(self, serve_name: str, cap: ServerCapabilities, editor):
        from lsp.lsp_interface import LanguageServerMixIn
        editor: LanguageServerMixIn
        print('run hook func, ', serve_name)
        for k in ['hover_provider',
                  'document_symbol_provider',
                  'references_provider',
                  'rename_provider',
                  'completion_provider',
                  'diagnostic_provider', ]:
            field = getattr(cap, k, None)
            flag = getattr(editor, editor.lsp_maps[k])
            if isinstance(field, (bool, None.__class__)):
                if field:
                    editor.support_enabled(flag)
                else:
                    print('disabled ', k)
                    editor.support_disabled(flag)
            else:
                if field:
                    editor.support_enabled(flag)
                else:
                    editor.support_disabled(flag)

    def dispatch_lsp_msg(self, msg: dict, lsp_serve_name: str, file_path: str = None):
        handler_lsp_msg(self, msg, lsp_serve_name, file_path)

    def lsp_root_uri(self):
        return str(self.r_run_time.current.resolve())

    def lsp_current_document_uri(self) -> str:
        return f'file:///{self.current_file_path()}'

    model: FileSystemModel = None
    plugins: Collections  # type hint
    fdb: QFontDatabase  # type hint
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
        self.load_fonts()
        self.init_signal_manager()

    def render_style_sheet(self):
        self.tabWidget.setFont(QFont('微软雅黑'))

    def render_custom_style(self):
        self.setAutoFillBackground(True)
        palette = self.palette()  # type: QPalette
        palette.setColor(QPalette.Window, QColor(current_styles.background_lighter))
        palette.setColor(QPalette.Foreground, QColor(current_styles.foreground))
        self.setPalette(palette)
        self.root
        if typing.TYPE_CHECKING:
            from pyqt5utils.components import TitleWidget
            self.root: TitleWidget
        self.root.setTitleBarColor(QColor(current_styles.title_background))
        self.menubar.setStyleSheet(
            'QMenuBar{background:%s;color:%s;border-top:1px solid %s;border-bottom: 0px solid %s}' % (
                current_styles.menubar_background, current_styles.foreground, current_styles.border,
                current_styles.border
            ))
        self.toolbar.setStyleSheet(
            'QToolBar{background:%s;color:%s;border-top:1px solid %s;border-bottom:1px solid %s;}'
            # 'QToolBar::separator{width:1px; color:red;}'
            % (
                current_styles.toolbar_background, current_styles.foreground, current_styles.border,
                current_styles.border,  # current_styles.border
            ))
        self.widget.setStyleSheet(
            'QWidget{background:%s;color:%s;border-top:1px solid %s;border-bottom: 0px solid %s}' % (
                current_styles.left_background, current_styles.foreground, current_styles.border,
                current_styles.border
            ))
        self.update()

    @cached_property
    def basic_fm(self):
        return QFontMetrics(QFont('微软雅黑', 10))

    def init_run_time(self):
        self.r_run_time: AppRunTime = AppRunTime()

    def load_menu_bar(self):
        pass

    def load_tool_bar(self):
        self.toolbar = self.addToolBar('File')
        self.static_toolbar_indexs = []
        self.dynamic_toolbar_actions = []
        cl = sorted(self.plugins.toolbar_actions, key=lambda k: self.plugins.toolbar_actions[k]['index'])
        for index, clz in enumerate(cl):
            self.static_toolbar_indexs.append(index)
            v = self.plugins.toolbar_actions.get(clz)
            tool_tip, icon = v.get('tool_tip'), v.get('icon')
            action_provider = clz(self)
            action = action_provider.make_action(icon, tool_tip, self)
            if isinstance(action, QAction):
                action.triggered.connect(lambda e, ac=action_provider: ac.action_slot())
                self.toolbar.addAction(action)
            elif isinstance(action, list):
                for widget in action:
                    ac = widget
                    if ac is None:
                        self.toolbar.addSeparator()
                    elif isinstance(ac, QAction):
                        ac.triggered.connect(lambda e, ac=action_provider: ac.action_slot())
                        self.toolbar.addAction(ac)
                    else:
                        self.toolbar.addWidget(ac)
        basic_fm = self.basic_fm
        height = basic_fm.height() * 1.8
        icon_size = basic_fm.height()
        self.toolbar.setIconSize(QSize(icon_size, icon_size))
        self.toolbar.setFixedHeight(height)

    def load_status(self):
        cl = sorted(self.plugins.status, key=lambda k: self.plugins.status[k]['index'])
        for clz in cl:
            widget = clz()
            self.statusbar.addPermanentWidget(widget)

    def load_fonts(self):
        self.fdb = QFontDatabase()
        fts = DirFontLoader.load(self.fdb, './')
        self.r_run_time.font_src.extend(fts)
        # print(self.r_run_time.font_src)

    def after_init(self):
        add_styled(self.tabWidget, 'tab')
        add_styled(self, 'custom-style')
        add_styled(self.statusbar, 'status-bar')
        add_styled(qApp, 'qApp')

        self.set_provider('main_app', self)
        self.start_lsp_server('pylsp', str(Path.cwd().resolve()))
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

        def _create_hook_file_and_open(file_path: str, file_content: str):
            path = Path(file_path)
            if not path.exists():
                path.touch()
                path.write_text(file_content, encoding='utf-8')
            self.open_file(file_path)

        def _open_project_file(file_path):
            self.open_file(file_path)

        def _open_file_and_move(file_path, line=None, col=None):
            self.open_file(file_path, line, col)

        def _run_lsp_hook(serve_name: str):
            from widgets.tabs.helpers import get_code_refs
            for k, code in get_code_refs().items():
                QApplication.processEvents()
                try:
                    if code.code_container.lsp_serve_name() == serve_name:
                        run_lsp_hook(serve_name, code)
                except:
                    import traceback
                    traceback.print_exc()

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
        signal_manager.add_event(signal_manager.runLspHook, None, call_back=_run_lsp_hook)
        self.sm = signal_manager

    def init_project(self):

        def remove_tab(index):
            widget = self.tabWidget.widget(index)
            widget.when_remove()
            self.tabWidget.removeTab(index)

        def tab_widget_change(index):
            # self.logger.info(f'index change: {index}')
            widget = self.tabWidget.widget(index)
            if widget:
                for dynamic in self.dynamic_toolbar_actions:
                    self.toolbar.removeAction(dynamic)
                self.dynamic_toolbar_actions.clear()
                actions = widget.create_dynamic_actions()
                if not isinstance(actions, (tuple, list)):
                    if actions is None:
                        actions = []
                    else:
                        actions = [actions]
                for index, action in enumerate(actions):
                    if isinstance(action, QAction):
                        self.toolbar.addAction(action)
                        self.dynamic_toolbar_actions.append(action)
                    elif action is None:
                        self.toolbar.addSeparator()
                    else:
                        a = QWidgetAction(self.toolbar)
                        a.setDefaultWidget(action)
                        self.toolbar.addAction(a)
                        self.dynamic_toolbar_actions.append(a)
            else:
                for dynamic in self.dynamic_toolbar_actions:
                    self.toolbar.removeAction(dynamic)
                self.dynamic_toolbar_actions.clear()

        self.tabWidget.tabCloseRequested.connect(remove_tab)
        self.tabWidget.currentChanged.connect(tab_widget_change)

        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([200, 500])

        self.setWindowTitle(self.app_name)
        self.setWindowIcon(QIcon(r'D:\work\httpfile\sources\编辑.svg'))

    def load_left(self):
        self.left_buttons = QButtonGroup()
        conf_key = self.config_name('left_splitter_sizes')

        def _splitter_moved(pos, handle_index):
            if handle_index == 1:
                current = self.splitter.widget(0).currentWidget()
                if not current.isVisible():
                    current.show()

        def switch_to(target: QWidget, index):
            if target.isVisible():
                self.settings.setValue(conf_key, self.splitter.sizes())
                target.hide()
                self.splitter.setSizes([0, 1000])
            else:
                target.show()
                sizes = self.splitter.sizes()
                if sizes[0] <= 0:
                    # sizes = [200, 1000]
                    sizes = self.settings.value(conf_key) or [200, 1000]
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

    ####  tab ####
    def add_tab_widget(self, file_type, file_name, file_path: str, url: str = None, content: str = None):
        icon = IconProvider.get_icon(file_name)
        if url is None:
            def _create_tab_code_widget():
                for k, v in self.plugins.tabs.items():
                    if file_type in v:
                        tab_ = k()
                        tab_.is_remote = False
                        if typing.TYPE_CHECKING:
                            from widgets.tabs import TabCodeWidget
                            tab_: TabCodeWidget
                        if tab_.support_code and tab_.code.support_language_parse:
                            self.start_lsp_server(tab_.lsp_serve_name(), str(self.r_run_time.current.resolve()))
                        # if tab_.support_code:
                        #     flag = tab_.code.register_to_app(self)
                        #     if flag:
                        #         lsp_name = tab_.code.lsp_serve_name()
                        #         # important
                        #         self.get_client(lsp_name)
                        #         self.lsp_initial(lsp_name, tab_)
                        tab_.load_file(file_path)
                        return tab_

            tab: ITabInterFace = _create_tab_code_widget()
            if tab:
                tab.set_read_only(self.r_run_time.read_only)
                tab_index = self.tabWidget.addTab(tab, icon, file_name)
                self.tabWidget.setCurrentWidget(tab)
                self.tabWidget.setTabToolTip(tab_index, file_path)

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
                tab_index = self.tabWidget.addTab(tab, icon, url)
                self.tabWidget.setCurrentWidget(tab)
                self.tabWidget.setTabToolTip(tab_index, file_path)

            return tab

    def current_tab(self):
        widget = self.tabWidget.currentWidget()
        if widget:
            return widget

    def file_has_open(self, file_path: str) -> bool:
        count = self.tabWidget.count()
        for i in range(count):
            tab = self.tabWidget.widget(i)
            if tab:
                if tab.file_path().replace('\\', '/') == file_path.replace('\\', '/'):
                    return True
        return False

    def open_file(self, file_path: str, line: int = None, col: int = None):
        path = Path(file_path)
        file_name = path.name
        file_type = path.suffix.replace('.', '', 1) + ' File'
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            print(widget.file_path().__class__, file_path.__class__)
            if widget.file_path().replace('\\', '/') == file_path.replace('\\', '/'):
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
        pos = self.mapToGlobal(self.pos())
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
        cls.plugins = plugins
        app = QApplication(sys.argv)
        mainapp = cls()
        mainapp.show()
        app.exec_()


run = MainWidget.run
