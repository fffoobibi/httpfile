from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from widgets.bottom_control import register
from ui.web_serverui import Ui_Form

from . import BottomWidgetMixIn
from widgets.base import PluginBaseMixIn
from widgets.web_worker import web_server_run


@register(name='web服务', icon=':/icon/API.svg', index=1)
class WebControlWidget(QWidget, Ui_Form, BottomWidgetMixIn, PluginBaseMixIn):
    check_state_signal = pyqtSignal(bool)

    def __init__(self):
        super(WebControlWidget, self).__init__()
        self.setupUi(self)
        self.set_slot()
        self.process_id = None

    def set_slot(self):
        self.pushButton.clicked.connect(self.start_web_task)
        self.pushButton_2.clicked.connect(self.stop_web_task)

    def start_web_task(self):
        from widgets.mainwidget import MainWidget
        main_app: MainWidget = self.gp('main_app')
        web_server_path = main_app.r_run_time.current
        print('web server path ', web_server_path)
        self.process_id = web_server_run(web_server_path.__str__())

    def stop_web_task(self):
        if self.process_id is not None:
            self.process_id.terminate()
            self.process_id = None

    def when_app_exit(self, main_app):
        print('close web task')
        self.stop_web_task()