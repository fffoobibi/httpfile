import jedi

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QApplication
from cached_property import cached_property

from widgets.base import PluginBaseMixIn
from widgets.signals import signal_manager
from widgets.factorys import styled_factory

from . import register


class JediHelper(object):

    @classmethod
    def get_python_info(cls):
        env = jedi.get_default_environment()
        info = env.version_info
        return f'Python {info.major}.{info.minor}.{info.micro}'

    @classmethod
    def get_python_default_env(cls):
        env = jedi.get_default_environment()
        return env


@register(name='', index=2)
class LockBtn(QPushButton, PluginBaseMixIn, styled_factory('bottom-button')):

    def __init__(self):
        super(LockBtn, self).__init__()
        self.setCheckable(True)
        self.setText(JediHelper.get_python_info())
        self.clicked.connect(self.click_slot)
        self.set_provider('python_info', JediHelper.get_python_default_env())
        self.setStyleSheet('color:red')

    def click_slot(self):
        from widgets.mainwidget import MainWidget
        main_app: MainWidget = self.get_app()
        print(main_app.get_python_info().__class__)
        # if self.isChecked():
        #     self.setIcon(QIcon(self._lock))
        #     lock = True
        # else:
        #     self.setIcon(QIcon(self._un_lock))
        #     lock = False
