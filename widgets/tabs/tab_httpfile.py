from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QListView, QVBoxLayout, QToolButton, QSpacerItem, QSizePolicy

from pyqt5utils.qsci.lexers.http_file import HttpFileLexer, CustomStyles
from . import register, TabCodeWidget


class HttpFileStyles(CustomStyles):
    request = 0  # 1, 0b0001
    header = 1  # 2, 0b0010
    data = 2  # 4, 0b0100
    response = 3
    key = 4
    request_url = 5
    splitter = 6
    black = 7
    section = 8
    chinese = 12
    output = 13

    # font flags
    underline = 9
    italic = 10
    bold = 11

    @classmethod
    def generate_styles(cls) -> Dict[int, str]:
        dic = {}
        for k, v in cls.__members__.items():
            dic[v.value] = k
        return dic

    @classmethod
    def defaultColor(cls, style: int):
        if style == cls.request:
            return QColor('#000000')
        elif style == cls.header:
            return QColor('#7F0C82')  # 紫色
        elif style == cls.section:
            return QColor('#CC6600')
        elif style == cls.data:
            return QColor('#CC0000')
        elif style == cls.response:
            return QColor(Qt.black)
        elif style == cls.key:  # request keyword
            return QColor('#044DCA')
        elif style == cls.request_url:  # request url
            return QColor('#ED673E')  # 橘色
        elif style == cls.splitter:  # splitter ###
            return QColor(Qt.gray)
        elif style == cls.black:
            return QColor(Qt.black)
        elif style == cls.output:
            return QColor(Qt.darkGray)

    @classmethod
    def defaultPaper(cls, style: int):
        if style == cls.request:
            return QColor('#FFEECC')
        elif style == cls.black:
            return QColor(Qt.white)
        elif style == cls.output:
            return QColor('#FFFAE3')

    @classmethod
    def defaultFont(cls, style: int, font: QFont):
        if style == cls.underline:
            font.setUnderline(True)
        if style == cls.bold:
            font.setBold(True)
        if style == cls.italic:
            font.setItalic(True)
        if style == cls.chinese:
            font = QFont('宋体', 10)
        if style == cls.request_url:
            font.setItalic(True)
        elif style == cls.key:
            font.setBold(True)
        elif style == cls.header:
            font.setItalic(True)
        elif style == cls.output:
            font.setItalic(True)
            font.setUnderline(True)
            font.setBold(True)
        return font


class TabHttpLexer(HttpFileLexer):
    styles_class = HttpFileStyles


@register(file_types=['http'])
class HTTPFileCodeWidget(TabCodeWidget):

    def set_lexer(self) -> Any:
        return TabHttpLexer(self)

    def set_splitter_widgets(self) -> List[QWidget]:
        return [
            QListView()
        ]

    def set_splitter_handle(self, index):
        if index == 1:
            handler = self.splitter.handle(1)
            handler.setCursor(Qt.SizeHorCursor)
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            button = QToolButton(handler)
            button.setArrowType(Qt.RightArrow)
            layout.addWidget(button)
            layout.addSpacerItem(QSpacerItem(20, 20, vPolicy=QSizePolicy.Expanding))
            handler.setLayout(layout)
