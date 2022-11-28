from datetime import datetime
from pathlib import Path

import uvicorn
from PyQt5.QtCore import pyqtSignal, Qt, QRegularExpression, QRegularExpressionMatchIterator
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtWidgets import QWidget
from fastapi import FastAPI
from flask import Flask, request

from pyqt5utils.components.styles import StylesHelper
from ui.web_serverui import Ui_Form
from widgets.base import PluginBaseMixIn
from widgets.bottom_control import BottomWidgetMixIn
from widgets.bottom_control import register
from widgets.factorys import styled_factory
from widgets.net_utils import get_host_ip
from widgets.signals import ProcessSignalMixIn, ProcessSignalMixInHelper
from widgets.styles import current_styles
from widgets.utils import ConfigProvider, ConfigKey


class FlaskWebWorker(ProcessSignalMixIn):
    event_name = 'flask-webserver'

    def _time_now(self):
        return f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

    def fork_func(self, queue, static_folder: str, port=9529):
        app = Flask(__name__, static_folder=static_folder, static_url_path='/')
        replace_name = Path(static_folder).__str__()
        local_ip = get_host_ip()
        self.push_msg(queue, f' * Running on all addresses (0.0.0.0)')
        self.push_msg(queue, f' * Running on http://127.0.0.1:{port}')
        self.push_msg(queue, f' * Running on http://{local_ip}:{port}')

        def _process(current: Path):
            dirs = list(current.iterdir())
            root = {}
            top_path = current.__str__().replace(replace_name, '')
            dirs.sort(key=lambda e: 0 if e.is_dir() else 1)
            for d in dirs:
                if d.is_file():
                    v = root.setdefault(top_path, [])
                    v.append(d.__str__().replace(replace_name, ''))
                else:
                    v = root.setdefault(top_path, [])
                    v.append(_process(d))
            if not dirs:
                root.setdefault(top_path, [])

            return root

        @app.get('/')
        def index():
            current = Path(static_folder)
            ret = _process(current)
            msg = ' * ' + self._time_now() + ' ' + request.remote_addr + ' -- ' + ' GET / HTTP/1.1 200'
            self.push_msg(queue, msg)
            return dict(code=0, data=ret)

        app.run(host='0.0.0.0', port=port, debug=False)


class FastApiWebWorker(ProcessSignalMixIn):
    event_name = 'fast-webserver'

    def _time_now(self):
        return f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

    def fork_func(self, queue, static_folder: str, port=9529):
        from fastapi.staticfiles import StaticFiles
        from fastapi import Request, WebSocket
        app = FastAPI()
        app.mount('/static', StaticFiles(directory=static_folder), 'public')

        replace_name = Path(static_folder).__str__()
        local_ip = get_host_ip()
        self.push_msg(queue, f' * Running on all addresses (0.0.0.0)')
        self.push_msg(queue, f' * Running on http://127.0.0.1:{port}')
        self.push_msg(queue, f' * Running on http://{local_ip}:{port}')

        def _process(current: Path):
            dirs = list(current.iterdir())
            root = {}
            top_path = current.__str__().replace(replace_name, '')
            dirs.sort(key=lambda e: 0 if e.is_dir() else 1)
            for d in dirs:
                if d.is_file():
                    v = root.setdefault(top_path, [])
                    v.append(d.__str__().replace(replace_name, ''))
                else:
                    v = root.setdefault(top_path, [])
                    v.append(_process(d))
            if not dirs:
                root.setdefault(top_path, [])

            return root

        # @app.on_event("startup")
        # async def startup_event():
        #     logger = logging.getLogger("uvicorn")
        #     handler = logging.handlers.RotatingFileHandler("api.log", mode="a", maxBytes=100 * 1024, backupCount=3)
        #     handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        #     logger.addHandler(handler)

        @app.get('/')
        def index(request: Request):
            current = Path(static_folder)
            ret = _process(current)
            msg = ' * ' + self._time_now() + ' ' + request.client.host + ' -- ' + ' GET / HTTP/1.1 200'
            self.push_msg(queue, msg)
            return dict(code=0, data=ret)

        @app.websocket_route('/ws')
        async def websocket(websocket: WebSocket):
            while True:
                json = await websocket.receive_json()
                await websocket.send_json('{"gg": "fuck you"}')

        uvicorn.run(app, reload=False, port=port, host='0.0.0.0')


class WebTextBrowserHighlighter(QSyntaxHighlighter):
    formatters = {}
    rules = []

    def __init__(self, parent):
        super(WebTextBrowserHighlighter, self).__init__(parent)
        self.init_formatters_and_rules()

    def init_formatters_and_rules(self):
        self.rules = [
            ('http', r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            ('info_http', r'\d+?[.]\d+?[.]\d+?[.]\d+'),
            ('info_time', r'\d+?-\d+?-\d+? \d+?:\d+?:\d+'),  # 2022-11-01 11:21:54
            ('info_status', r'(?<=HTTP/1.1 )\d+'),
            ('fold_info', r'(?<=run server fold at: ).*')
        ]
        baseFormat = QTextCharFormat()

        http_format = QTextCharFormat(baseFormat)
        http_format.setFontUnderline(True)
        http_format.setForeground(QColor(Qt.blue))
        self.formatters['http'] = http_format

        info_http = QTextCharFormat(baseFormat)
        info_http.setFontUnderline(True)
        info_http.setForeground(QColor(Qt.blue))
        self.formatters['info_http'] = info_http

        info_time = QTextCharFormat(baseFormat)
        info_time.setForeground(QColor(Qt.darkGreen))
        self.formatters['info_time'] = info_time

        info_status = QTextCharFormat(baseFormat)
        info_status.setFontWeight(QFont.Bold)
        info_status.setForeground(QColor(Qt.red))
        self.formatters['info_status'] = info_status

        fold_info = QTextCharFormat(baseFormat)
        fold_info.setFontWeight(QFont.Bold)
        fold_info.setForeground(QColor(Qt.black))
        self.formatters['fold_info'] = fold_info

    def highlightBlock(self, text: str) -> None:
        for name, rule in self.rules:
            expression = QRegularExpression(rule)
            iterator: QRegularExpressionMatchIterator = expression.globalMatch(text)
            while iterator.hasNext():
                # print('find compact', name)
                match = iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                # value = match.captured()
                self.setFormat(start, length, self.formatters[name])


@register(name='WEB服务', icon=':/icon/API.svg', index=1)
class WebControlWidget(QWidget, Ui_Form, BottomWidgetMixIn, PluginBaseMixIn, ProcessSignalMixInHelper,
                       styled_factory('background-darker')):
    check_state_signal = pyqtSignal(bool)
    append_signal = pyqtSignal(str)

    horizontal = ConfigProvider.default(ConfigKey.general, 'horizontal_height')
    vertical = ConfigProvider.default(ConfigKey.general, 'vertical_width')

    web_worker_class = FastApiWebWorker

    def render_custom_style(self):
        border = current_styles.border
        # self.widget.setStyleSheet('.QWidget{border:1px solid %s}' % border)
        self.widget.setStyleSheet('.QWidget{border:1px solid %s}' % border)

    def __init__(self):
        super(WebControlWidget, self).__init__()
        self.setupUi(self)
        self.set_slot()
        self.process_id = None
        self.process_queue = None
        self.current_thread = None

    def after_init(self):
        self.pushButton_3.hide()
        self.pushButton_2.setEnabled(False)
        # self.hilighter = WebTextBrowserHighlighter(self.textBrowser.document())
        self.textBrowser.setStyleSheet('border: none')
        self.append_signal.connect(self.textBrowser.append)

        StylesHelper.set_v_history_style_dynamic(self.textBrowser, color='#CFCFCF', background='transparent',
                                                 width=self.vertical.value)
        StylesHelper.set_h_history_style_dynamic(self.textBrowser, color='#CFCFCF', background='transparent',
                                                 height=self.horizontal.value)

    def set_slot(self):
        self.pushButton.clicked.connect(self.start_web_task)
        self.pushButton_2.clicked.connect(self.stop_web_task)
        self.pushButton_5.clicked.connect(self.clear_output)

    def clear_output(self):
        self.textBrowser.clear()

    def start_web_task(self):
        try:
            if self.process_id is None and self.current_thread is None:
                self.textBrowser.clear()
                from widgets.mainwidget import MainWidget
                main_app: MainWidget = self.gp('main_app')
                web_server_path = main_app.r_run_time.current
                event_name = self.web_worker_class.event_name
                self.textBrowser.append(f'run server fold at: {web_server_path.__str__()}\n')
                self.process_id, self.process_queue = self.web_worker_class().fork(event_name,
                                                                                   web_server_path.__str__())
                self.current_thread = self.start_msg_loop(self.process_queue)
                self.pushButton.hide()
                self.pushButton_3.show()
                self.pushButton_2.setEnabled(True)
            else:
                self.pushButton.show()
                self.pushButton_3.hide()
                self.pushButton_2.setEnabled(False)
        except:
            import traceback
            traceback.print_exc()
            raise

    def stop_web_task(self):
        if self.process_id is not None:
            self.process_id.terminate()
            self.kill_msg_loop()
            self.process_id = None
            self.process_queue = None
            self.current_thread = None

            self.pushButton.show()
            self.pushButton_2.setEnabled(False)
            self.pushButton_3.hide()
        else:
            pass

    def when_app_exit(self, main_app):
        self.stop_web_task()

    def when_accept_process_msg(self, msg: str):
        self.append_signal.emit(msg + '\n')
