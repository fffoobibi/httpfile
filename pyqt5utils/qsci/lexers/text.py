from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from pyqt5utils.qsci.base import BaseCodeWidget, Lexers


class TextCodeWidget(BaseCodeWidget):
    type = Lexers.text

