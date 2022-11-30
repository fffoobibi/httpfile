import re
from types import MethodType

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QProgressBar, QVBoxLayout, QWidget, QLineEdit

from widgets.base import PluginBaseMixIn
from widgets.factorys import styled_factory
from widgets.left_control import register
from widgets.styles import current_styles

browser_icon = ':/icon/browser.svg'


@register('浏览器', index=2, icon=browser_icon)
class WebEngineView(QWidget, PluginBaseMixIn, styled_factory('custom-style')):

    def render_custom_style(self):
        background = current_styles.background_lighter
        foreground = current_styles.foreground
        border = current_styles.border
        self.url_line.setStyleSheet('QLineEdit{background: %s;color:%s;padding:4px;font-family:微软雅黑;border:1px solid %s}' % (
            background, foreground, border
        ))

    def __init__(self):
        super(WebEngineView, self).__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(1, 1, 1, 1)
        lay.setSpacing(0)
        self.url_line = QLineEdit()
        self.url_line.setClearButtonEnabled(True)
        self.url_line.setPlaceholderText('输入网址')

        self.progress = QProgressBar()
        self.progress.setFixedHeight(8)
        self.progress.setFormat('')
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.hide()
        self.progress.setRange(0, 100)

        self.browser = QWebEngineView()
        lay.addWidget(self.url_line)
        lay.addWidget(self.progress)
        lay.addWidget(self.browser)

        self.browser.loadStarted.connect(self.when_page_start)
        self.browser.loadFinished.connect(self.when_page_finished)
        self.browser.loadProgress.connect(self.when_page_loaded)
        self.url_line.returnPressed.connect(self.go_to)

        def create_window(this, window_type):
            return this

        self.browser.createWindow = MethodType(create_window, self.browser)

    def go_to(self):
        text = self.url_line.text().strip()
        if text:
            try:
                # re.sub(r'(https://)')
                if (text.startswith('https://') is False) and (text.startswith('http://') is False):
                    text = f'http://{text}'
                    self.url_line.setText(text)
                self.browser.load(QUrl(text))
            except:
                pass

    def when_page_start(self):
        self.progress.show()

    def when_page_loaded(self, progress):
        self.progress.show()
        if progress == 0:
            self.progress.setValue(progress + 1)
        else:
            self.progress.setValue(progress)

    def when_page_finished(self, finished):
        self.progress.setValue(0)
        self.progress.hide()
