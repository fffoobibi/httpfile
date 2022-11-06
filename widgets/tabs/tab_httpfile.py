from types import MethodType
from typing import Any, Dict, List

from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QFont, QMouseEvent, QCursor
from PyQt5.QtWidgets import QWidget, QListView, QVBoxLayout, QToolButton, QSpacerItem, QSizePolicy, QListWidget, \
    QListWidgetItem, QApplication, QLabel, QToolTip

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
    variable = 14

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
            return QColor('red')
        elif style == cls.request_url:  # request url
            return QColor('blue')  # 橘色
        elif style == cls.splitter:  # splitter ###
            return QColor(Qt.gray)
        elif style == cls.black:
            return QColor(Qt.black)
        elif style == cls.output:
            return QColor('#2D8C00')
        elif style == cls.variable:
            return QColor(Qt.darkBlue)

    @classmethod
    def defaultPaper(cls, style: int):
        if style == cls.request:
            return QColor('#FFEECC')
        elif style == cls.black:
            return QColor(Qt.white)
        elif style == cls.output:
            return QColor('#EDFCED')

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
        elif style == cls.variable:
            font.setItalic(True)
            # font.setBold(True)
        return font


class TabHttpLexer(HttpFileLexer):
    styles_class = HttpFileStyles


def code_mouseMoveEvent(self, a0: QMouseEvent) -> None:
    self.__class__.mouseMoveEvent(self, a0)
    point = a0.pos()
    position = self.positionFromPoint(point)
    if self.hasIndicator(self.lexer().url_indicator, position):
        QToolTip.showText(QCursor.pos(), 'ctrl+点击跳转网页')
    else:
        QToolTip.hideText()


@register(file_types=['http'])
class HTTPFileCodeWidget(TabCodeWidget):
    url_indicator_signal = pyqtSignal(int, int, int, int, str)  # line, index, position, value, text

    def __init__(self):
        super(HTTPFileCodeWidget, self).__init__()
        self.code.setMouseTracking(True)
        self.code.mouseMoveEvent = MethodType(code_mouseMoveEvent, self.code)

    def set_lexer(self) -> Any:
        return TabHttpLexer(self)

    def add_url_item(self, line, col, position, value, text):
        content = text.split(' ')
        method = content[0]
        url = ' '.join(content[1:]).strip()
        print('get value ', line, value)
        if value not in self.listview._item_values:
            listview = self.listview
            item = QListWidgetItem()
            item.setData(Qt.UserRole, value)
            item.setData(Qt.UserRole + 1, line)
            item.setSizeHint(QSize(24, 50))
            label = QLabel()
            label.setIndent(4)
            label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            label.setText(f'<font weight="bold">{line + 1}. </font><font color="red"><b>{method}</font></b> {url}')
            listview.addItem(item)
            listview.setItemWidget(item, label)
            listview._item_values.add(value)
        else:
            for i in range(self.listview.count()):
                QApplication.processEvents()
                item = self.listview.item(i)
                if item.data(Qt.UserRole) == value:
                    label = self.listview.itemWidget(item)
                    label.setText(
                        f'<font weight="bold">{line + 1}. </font><font color="red"><b>{method}</font></b> {url}')
                    return

    def go_to_indicator(self, item: QListWidgetItem):
        line = item.data(Qt.UserRole + 1)
        col = 0
        self.move_to(line, col)

    def set_splitter_widgets(self) -> List[QWidget]:
        self.listview = listview = QListWidget()
        self.listview._item_values = set()
        self.url_indicator_signal.connect(self.add_url_item)
        self.listview.itemClicked.connect(self.go_to_indicator)
        return [
            listview
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
            # layout.addSpacerItem(QSpacerItem(20, 20, vPolicy=QSizePolicy.Expanding))
            handler.setLayout(layout)

    def when_modify(self, position, modificationType, text, length, linesAdded,
                    line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded):
        super(HTTPFileCodeWidget, self).when_modify(position, modificationType, text, length, linesAdded, line,
                                                    foldLevelNow, foldLevelPrev, token, annotationLinesAdded)
        full = self.code.SC_MOD_INSERTTEXT | self.code.SC_MOD_DELETETEXT
        if (~modificationType & full == full):
            return
        # print('linesadded , ', linesAdded, 'len,', length, 'line, ', token)
        # from PyQt5 import QsciScintilla
        # code: QsciScintilla
        code = self.code
        lexer = code.lexer()
        cline, col = self.code.lineIndexFromPosition(position)
        if code.hasIndicator(lexer.url_indicator, position - 1):
            line_text = code.text(cline)
            indicator_value = code.SendScintilla(code.SCI_INDICATORVALUEAT, lexer.url_indicator,
                                                 position - 1)
            self.url_indicator_signal.emit(cline, col, position - 1, indicator_value, line_text.strip())
        else:
            if linesAdded:
                pass
