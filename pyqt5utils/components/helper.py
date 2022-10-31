from types import MethodType

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLineEdit, QApplication


class ObjectsHelper(QObject):

    @classmethod
    def window_size(cls):
        app = QApplication.desktop()
        geo = app.screenGeometry()
        return geo.width(), geo.height()
        
    @classmethod
    def set_fmheight(cls, target: QWidget, scaled: float = 1.5, value: int = 0):
        fm = target.fontMetrics()
        height = fm.height() * scaled + value
        target.setFixedHeight(height)
        return height

    @classmethod
    def set_fmwidth(cls, target: QWidget, content: str, scaled: float = 1.0, value: int = 0):
        fm = target.fontMetrics()
        width = fm.width(content) * scaled + value
        target.setFixedWidth(width)
        return width

    @classmethod
    def set_double_validator(cls, line: QLineEdit, min_=0, max_=9999999999, digit=2) -> QDoubleValidator:
        def _currentText(this):
            return this.__class__.text(this).replace(',', '').strip()

        validator = QDoubleValidator(min_, max_, digit)
        validator.setNotation(QDoubleValidator.StandardNotation)
        line.setValidator(validator)
        line.text = MethodType(_currentText, line)
        return validator
