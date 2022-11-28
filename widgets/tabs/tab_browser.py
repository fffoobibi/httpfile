from types import MethodType
from typing import List

from PyQt5.QtCore import QUrl, pyqtSignal, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar

from . import register, TabCodeWidget


class WebEngineView(QWidget):
    def __init__(self):
        super(WebEngineView, self).__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.progress = QProgressBar()
        self.progress.setFixedHeight(8)
        self.progress.setFormat('')
        self.progress.setAlignment(Qt.AlignCenter)
        self.browser = QWebEngineView()
        lay.addWidget(self.progress)
        lay.addWidget(self.browser)

        self.progress.setRange(0, 100)
        # self.browser.loadStarted.connect(self.when_page_start)
        self.browser.loadFinished.connect(self.when_page_finished)
        self.browser.loadProgress.connect(self.when_page_loaded)

        def create_window(this, window_type):
            return this

        self.browser.createWindow = MethodType(create_window, self.browser)

    def when_page_loaded(self, progress):
        if progress == 0:
            self.progress.setValue(progress + 1)
        else:
            self.progress.setValue(progress)

    def when_page_finished(self, finished):
        self.progress.setValue(0)


@register(file_types=['html'])
class WebEngineWidget(TabCodeWidget):
    support_code = False
    file_loaded = pyqtSignal()
    file_type = 'html'

    def set_splitter_widgets(self) -> List[QWidget]:
        web_engine = WebEngineView()
        self.web_engine = web_engine
        return [web_engine]

    def after_init(self):
        self.file_loaded.connect(self.when_file_loaded)

    def when_file_loaded(self):
        # self.web_engine.browser.load(QUrl('https://www.tiktok.com'))
        # self.web_engine.browser.load(QUrl('http://127.0.0.1:8888/?token=99e89de9f87b4ccef02ed064fe4020b281068543d9905e5f'))
        self.web_engine.browser.load(QUrl.fromLocalFile(f'{self.file_path()}'))
