import subprocess
import threading
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItem, QFont, QFontMetrics
from PyQt5.QtWidgets import QWidget, QButtonGroup, QTabBar
from cached_property import cached_property

from ui.run_serverui import Ui_Form
from widgets.base import PluginBaseMixIn
from widgets.bottom_control import register
from widgets.types import Request
from widgets.utils import ConfigProvider, ConfigKey, IconProvider
from . import BottomWidgetMixIn
from .run_server_lexer import RunServerConsole
from ..factorys import add_styled, styled_factory
from ..styles import current_styles


class ConsoleTasks(object):
    lock = threading.RLock()
    tasks = {}

    @dataclass
    class result_class:
        path: str
        result: list
        returnCode: Optional[int]
        running: bool

    def task_is_running(self, file_path) -> bool:
        task = self.tasks.get(file_path)
        if task:
            return task.running
        return False

    def add_task(self, file_path):
        result = self.tasks.setdefault(file_path, self.result_class(path=file_path, result=[], returnCode=None, running=True))
        if result.running is False:
            result.result.clear()

    def task_done(self, file_path):
        task = self.tasks.get(file_path)
        if task:
            task.running = False

    def save_msg(self, file_path, msg: str):
        result = self.tasks[file_path]
        result.result.append(msg)

    def get_msg(self, file_path) -> str:
        result = self.tasks[file_path]
        return ''.join(result.result)

    def dispatch_msg(self, file_path, msg, obj: 'RunControlWidget'):
        index = obj.tab_bar.currentIndex()
        if index > -1:
            tooltip = obj.tab_bar.tabToolTip(index)
            if tooltip == file_path:
                obj.run_console.append(msg)


@register(name='运行', icon=':/icon/服务01.svg', index=3)
class RunControlWidget(QWidget, Ui_Form, BottomWidgetMixIn, PluginBaseMixIn, styled_factory('background-darker')):
    check_state_signal = pyqtSignal(bool)
    horizontal = ConfigProvider.default(ConfigKey.general, 'horizontal_height')
    vertical = ConfigProvider.default(ConfigKey.general, 'vertical_width')

    update_signal = pyqtSignal(QStandardItem, Request)

    run_signal = pyqtSignal(str, str)
    run_tasks_sets = set()
    run_tasks_procs = {}
    console_container_class = ConsoleTasks

    @cached_property
    def console_result(self):
        return self.console_container_class()

    @cached_property
    def run_console(self):
        return RunServerConsole(self)

    def render_custom_style(self):
        border = current_styles.border
        self.widget.setStyleSheet('.QWidget{border:1px solid %s}' % border)
        self.widget_2.setStyleSheet('.QWidget{border:1px solid %s}' % border)

    def _run_python(self, file_path, cmd: List):
        proc = subprocess.Popen(cmd, shell=False,
                                stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                )
        self.run_tasks_procs[file_path] = [proc]
        cmd = ' '.join(cmd)
        self.run_signal.emit(file_path, cmd + '\n')
        while True:
            msg = proc.stdout.readline()
            if msg == b'':
                break
            self.run_signal.emit(file_path, msg.decode('utf8'))
        proc.kill()
        proc.wait()
        self.run_signal.emit(file_path, f'\n进程已结束,退出代码 {proc.returncode}')
        self.console_result.task_done(file_path)
        try:
            self.run_tasks_sets.remove(file_path)
        except:
            pass
        self.run_tasks_procs[file_path].append(self.run_console.text())

    def add_run_tab(self, file_path):
        exists = None
        for i in range(self.tab_bar.count()):
            tab_tip = self.tab_bar.tabToolTip(i)
            if tab_tip == file_path:
                exists = i
                break
        if exists is None:
            file = Path(file_path)
            file_name = file.name.replace(".py", "")
            index = self.tab_bar.addTab(IconProvider.get_icon(file_path), file_name)
            self.tab_bar.setTabToolTip(index, file_path)
        else:
            self.tab_bar.setCurrentIndex(exists)

    def start_run_python(self):
        from widgets.mainwidget import MainWidget
        main_app: MainWidget = self.get_app()
        exec_path = main_app.get_python_info().executable
        current_file = main_app.current_file_path()
        if current_file and current_file.endswith('py'):
            self.run_console.clear()
            self.run_tasks_sets.add(current_file)
            self.console_result.add_task(current_file)
            self.add_run_tab(current_file)
            with suppress(Exception):
                proc = self.run_tasks_procs.get(current_file)
                proc.terminate()
                proc.wait()
            t = threading.Thread(target=self._run_python, args=(current_file, [exec_path, current_file]))
            t.start()

    def when_app_exit(self, main_app):
        for path, popen in self.run_tasks_procs.items():
            try:
                proc, result = popen
                proc.terminate()
                proc.wait()
            except:
                import traceback
                traceback.print_exc()

    def update_run_info(self, file_path, msg):
        self.console_result.dispatch_msg(file_path, msg, self)
        self.console_result.save_msg(file_path, msg)

    def __init__(self):
        super(RunControlWidget, self).__init__()
        self.setupUi(self)
        self.init_run_lexer()
        self.init_slots()
        self.button_groups = QButtonGroup()
        self.init_tab()

    def init_tab(self):
        def show_text(index):
            file_path = self.tab_bar.tabToolTip(index)
            msg = self.console_result.get_msg(file_path)
            self.run_console.clear()
            self.run_console.setText(msg)

        def close_tab(index):
            self.tab_bar.removeTab(index)

        self.tab_bar = QTabBar()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setMovable(True)
        self.tab_bar.tabCloseRequested.connect(close_tab)
        self.tab_bar.tabBarClicked.connect(show_text)
        self.horizontalLayout_2.insertWidget(0, self.tab_bar)
        add_styled(self.tab_bar, 'run-tab')
        fm = QFontMetrics(QFont('微软雅黑', 9))
        self.widget_2.setFixedHeight(fm.height() + 12)

    def init_slots(self):
        self.pushButton.clicked.connect(self.start_run_python)
        self.run_signal.connect(self.update_run_info)

    def init_run_lexer(self):
        self.verticalLayout.addWidget(self.run_console)
