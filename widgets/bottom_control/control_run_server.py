import subprocess
import subprocess
import threading
from pathlib import Path
from typing import List

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QStandardItem, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QButtonGroup
from cached_property import cached_property

from ui.run_serverui import Ui_Form
from widgets.base import PluginBaseMixIn
from widgets.bottom_control import register
from widgets.types import Request
from widgets.utils import ConfigProvider, ConfigKey
from . import BottomWidgetMixIn
from .run_server_lexer import RunServerConsole
from ..factorys import add_styled


@register(name='运行', icon=':/icon/服务01.svg', index=3)
class RunControlWidget(QWidget, Ui_Form, BottomWidgetMixIn, PluginBaseMixIn):
    check_state_signal = pyqtSignal(bool)
    horizontal = ConfigProvider.default(ConfigKey.general, 'horizontal_height')
    vertical = ConfigProvider.default(ConfigKey.general, 'vertical_width')

    update_signal = pyqtSignal(QStandardItem, Request)

    run_signal = pyqtSignal(str, str)
    run_tasks_sets = set()
    run_tasks_popens = {}

    def _run_python(self, file_path, cmd: List):
        popen = subprocess.Popen(cmd, shell=False,
                                 stdout=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 )
        self.run_tasks_popens[file_path] = popen
        cmd = ' '.join(cmd)
        self.run_signal.emit(file_path, cmd + '\n')
        while True:
            msg = popen.stdout.readline()
            if msg == b'':
                break
            self.run_signal.emit(file_path, msg.decode('utf8'))
        popen.wait()
        self.run_signal.emit(file_path, f'\n进程已结束,退出代码 {popen.returncode}')
        try:
            self.run_tasks_sets.remove(file_path)
        except:
            pass
        self.run_tasks_popens.pop(file_path, None)

    def add_run_tab(self, file_path):
        file = Path(file_path)
        btn = QPushButton()
        btn.setText(f'{file.name.replace(".py", "")}')
        btn.setCheckable(True)
        btn.setChecked(True)
        btn.setIcon(QIcon(':/icon/guanbi.svg'))
        btn.setLayoutDirection(Qt.RightToLeft)
        add_styled(btn, 'run-button')
        self.button_groups.addButton(btn)
        count = self.horizontalLayout_2.count()
        self.horizontalLayout_2.insertWidget(count - 1, btn)

    def start_run_python(self):
        from widgets.mainwidget import MainWidget
        main_app: MainWidget = self.get_app()
        exec_path = main_app.get_python_info().executable
        current_file = main_app.current_file_path()
        if current_file and current_file.endswith('py'):
            self.run_console.clear()
            self.run_tasks_sets.add(current_file)
            self.add_run_tab(current_file)
            try:
                popen = self.run_tasks_popens.get(current_file)
                popen.terminate()
                popen.wait()
            except:
                pass
            t = threading.Thread(target=self._run_python, args=(current_file, [exec_path, current_file]))
            t.start()

    def when_app_exit(self, main_app):
        for path, popen in self.run_tasks_popens.items():
            try:
                popen.terminate()
                popen.wait()
            except:
                import traceback
                traceback.print_exc()

    def update_run_info(self, file_path, msg):
        self.run_console.append(f'{msg}')

    def __init__(self):
        super(RunControlWidget, self).__init__()
        self.setupUi(self)
        self.init_run_lexer()
        self.init_slots()
        self.button_groups = QButtonGroup()

    def init_slots(self):
        self.pushButton.clicked.connect(self.start_run_python)
        self.run_signal.connect(self.update_run_info)

    @cached_property
    def run_console(self):
        return RunServerConsole(self)

    def init_run_lexer(self):
        self.verticalLayout.addWidget(self.run_console)
