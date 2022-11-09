from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QLabel

from pyqt5utils.components.styles import StylesHelper
from widgets.bottom_control import register
from widgets.base import PluginBaseMixIn
from widgets.signals import ProcessSignalMixInHelper, signal_manager
from widgets.utils import ConfigProvider, ConfigKey

from ui.api_serverui import Ui_Form
from . import BottomWidgetMixIn


# @register(name='web服务', icon=':/icon/API.svg', index=1)
# class WebControlWidget(QWidget, Ui_Form, BottomWidgetMixIn, PluginBaseMixIn, ProcessSignalMixInHelper):
#     check_state_signal = pyqtSignal(bool)
#     append_signal = pyqtSignal(str)
#
#     horizontal = ConfigProvider.default(ConfigKey.general, 'horizontal_height')
#     vertical = ConfigProvider.default(ConfigKey.general, 'vertical_width')
#
#     web_worker_class = FastApiWebWorker
#
#     def __init__(self):
#         super(WebControlWidget, self).__init__()
#         self.setupUi(self)
#         self.set_slot()
#         self.process_id = None
#         self.process_queue = None
#         self.current_thread = None
#
#     def after_init(self):
#         self.pushButton_3.hide()
#         self.pushButton_2.setEnabled(False)
#         # self.hilighter = WebTextBrowserHighlighter(self.textBrowser.document())
#         self.textBrowser.setStyleSheet('border: none')
#         self.append_signal.connect(self.textBrowser.append)
#
#         StylesHelper.set_v_history_style_dynamic(self.textBrowser, color='#CFCFCF', background='transparent',
#                                                  width=self.vertical.value)
#         StylesHelper.set_h_history_style_dynamic(self.textBrowser, color='#CFCFCF', background='transparent',
#                                                  height=self.horizontal.value)
#
#     def set_slot(self):
#         self.pushButton.clicked.connect(self.start_web_task)
#         self.pushButton_2.clicked.connect(self.stop_web_task)
#         self.pushButton_5.clicked.connect(self.clear_output)
#
#     def clear_output(self):
#         self.textBrowser.clear()
#
#     def start_web_task(self):
#         try:
#             if self.process_id is None and self.current_thread is None:
#                 self.textBrowser.clear()
#                 from widgets.mainwidget import MainWidget
#                 main_app: MainWidget = self.gp('main_app')
#                 web_server_path = main_app.r_run_time.current
#                 event_name = self.web_worker_class.event_name
#                 self.textBrowser.append(f'run server fold at: {web_server_path.__str__()}\n')
#                 self.process_id, self.process_queue = self.web_worker_class().fork(event_name,
#                                                                                    web_server_path.__str__())
#                 self.current_thread = self.start_msg_loop(self.process_queue)
#                 self.pushButton.hide()
#                 self.pushButton_3.show()
#                 self.pushButton_2.setEnabled(True)
#             else:
#                 self.pushButton.show()
#                 self.pushButton_3.hide()
#                 self.pushButton_2.setEnabled(False)
#         except:
#             import traceback
#             traceback.print_exc()
#             raise
#
#     def stop_web_task(self):
#         if self.process_id is not None:
#             self.process_id.terminate()
#             self.kill_msg_loop()
#             self.process_id = None
#             self.process_queue = None
#             self.current_thread = None
#
#             self.pushButton.show()
#             self.pushButton_2.setEnabled(False)
#             self.pushButton_3.hide()
#         else:
#             pass
#
#     def when_app_exit(self, main_app):
#         self.stop_web_task()
#
#     def when_accept_process_msg(self, msg: str):
#         self.append_signal.emit(msg + '\n')
#

class ApiCodeWidget(QWidget):
    pass


@register(name='服务', icon=':/icon/服务01.svg', index=2)
class ApiControlWidget(QWidget, Ui_Form, BottomWidgetMixIn, PluginBaseMixIn, ProcessSignalMixInHelper):
    check_state_signal = pyqtSignal(bool)
    horizontal = ConfigProvider.default(ConfigKey.general, 'horizontal_height')
    vertical = ConfigProvider.default(ConfigKey.general, 'vertical_width')

    def __init__(self):
        super(ApiControlWidget, self).__init__()
        self.setupUi(self)

    def after_init(self):
        def _set_title(st):
            self.label.setText(st)

        StylesHelper.set_v_history_style_dynamic(self.textBrowser.code_html.code, color='#CFCFCF',
                                                 background='transparent',
                                                 width=self.vertical.value)
        StylesHelper.set_h_history_style_dynamic(self.textBrowser.code_html.code, color='#CFCFCF',
                                                 background='transparent',
                                                 height=self.horizontal.value)

        self.splitter.setSizes([200, 1000])
        self.splitter.setChildrenCollapsible(0)
        self.splitter.widget(0).setMinimumWidth(0)
        self.splitter.widget(1).setMinimumWidth(40)
        self.splitter.handle(1).setCursor(Qt.SizeHorCursor)

        self.pushButton_6.clicked.connect(self.wrap_slot)
        self.pushButton_7.clicked.connect(self.hide_slot)
        self.pushButton_8.clicked.connect(self.clear_fold_slot)
        signal_manager.add_event('api_server_title', None, _set_title)

    def wrap_slot(self, checked):
        code = self.textBrowser.code
        if checked:
            code.setWrapMode(code.SC_WRAP_CHAR)
        else:
            code.setWrapMode(code.SC_WRAP_NONE)

    def hide_slot(self):
        self.get_app().hide_bottom_panel(1)

    def clear_fold_slot(self, checked):
        code = self.textBrowser.code
        if checked:
            code.clearFolds()
        else:
            code.foldAll()
