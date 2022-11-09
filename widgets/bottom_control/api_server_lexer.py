from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from cached_property import cached_property

from widgets.signals import signal_manager
from widgets.tabs.tab_html import HTMLCodeWidget


class ApiTextBrowser(QWidget):
    def __init__(self, *a, **kw):
        super(ApiTextBrowser, self).__init__(*a, **kw)
        self.lay = QVBoxLayout(self)
        self.lay.setSpacing(0)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.code_html = HTMLCodeWidget()
        self.lay.addWidget(self.code_html)
        self.init_code()

    def init_code(self):
        def _update(value):
            self.code.append(value + '\n')

        def _clear():
            self.code.clear()

        def _fold_all():
            self.code.foldAll()

        def _set_title():
            self.code

        self.code.setReadOnly(True)
        # self.code.setMargins(0)
        self.code.setUtf8(True)
        self.code.setCaretLineAlwaysVisible(False)
        self.code.setCaretForegroundColor(Qt.red)
        self.code.setCaretLineBackgroundColor(Qt.transparent)
        signal_manager.add_event('api_server_clear', None, _clear)
        signal_manager.add_event('api_server_out_put', None, _update)
        signal_manager.add_event('api_server_fold_all', None, _fold_all)

        # self.code.setMinimumWidth(self.code.marginWidth(0) + self.code.marginWidth(1) + 4)

    @cached_property
    def code(self):
        return self.code_html.code
