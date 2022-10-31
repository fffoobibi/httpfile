from PyQt5.QtWidgets import QWidget, QDialog

from .controllers import Base


class BaseWidget(Base, QWidget):
    pass


class BaseDialog(Base, QDialog):
    pass
