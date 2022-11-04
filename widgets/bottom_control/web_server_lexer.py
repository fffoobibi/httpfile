import re

try:
    from PyQt5 import QsciScintilla
except:
    from PyQt5.Qsci import QsciScintilla

from enum import auto

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QColor, QFont, QDesktopServices

from pyqt5utils.qsci.custom_lexer import CustomStyles, CustomLexerCompat
from pyqt5utils.qsci.scintillacompat import QsciScintillaCompat

from contextlib import suppress


class WebServerStyles(CustomStyles):
    http = 1
    info_http = auto()
    info_time = auto()
    info_status = auto()
    fold_info = auto()
    normal = auto()

    @classmethod
    def defaultColor(cls, style):
        if style == cls.http:
            return QColor('blue')
        elif style == cls.info_http:
            return QColor('red')
        elif style == cls.info_time:
            return QColor('green')
        elif style == cls.info_status:
            return QColor('red')
        elif style == cls.fold_info or style == cls.normal:
            return QColor('black')

    @classmethod
    def defaultPaper(cls, style):
        return QColor('white')

    @classmethod
    def defaultFont(cls, style, font: QFont):
        f = QFont('Consolas')
        f.setPointSize(font.pointSize())
        if style == cls.fold_info:
            f.setBold(True)
        return f


class WebServerConsoleLexer(CustomLexerCompat):
    language_desc = 'web-server console'
    styles_class = WebServerStyles
    url_ind = 0
    fold_ind = 1

    def __init__(self, parent):
        super(WebServerConsoleLexer, self).__init__(parent)
        self.define_indicators(self.parent())

    def define_indicators(self, editor: 'WebServerConsole'):
        def indicator_clicked(line, index, keys):
            position = editor.positionFromLineIndex(line, index)
            if editor.hasIndicator(self.url_ind, position):
                start = editor.getIndicatorStartPos(self.url_ind, position)
                end = editor.getIndicatorEndPos(self.url_ind, position)
                text = editor.text(start, end)
                is_url = True
            else:
                start = editor.getIndicatorStartPos(self.fold_ind, position)
                end = editor.getIndicatorEndPos(self.fold_ind, position)
                text = editor.text(start, end)
                is_url = False
            if is_url:
                QDesktopServices.openUrl(QUrl(text))
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(f'file:///{text}'))
            # Retrieve absolute position
            # position = editor.positionFromLineIndex(line, index)
            # Retrieve given value
            # value = editor.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT,
            #                              indicator_num, position)
            # start = editor.SendScintilla(QsciScintilla.SCI_INDICATORSTART, indicator_num, position)
            # end = editor.SendScintilla(QsciScintilla.SCI_INDICATOREND, indicator_num, position)

        editor.indicatorDefine(QsciScintilla.INDIC_COMPOSITIONTHIN, self.url_ind)
        editor.setIndicatorForegroundColor(QColor(Qt.blue))
        editor.setIndicatorHoverStyle(QsciScintilla.INDIC_COMPOSITIONTHICK, self.url_ind)
        editor.setIndicatorHoverForegroundColor(QColor(Qt.blue), self.url_ind)

        editor.indicatorDefine(QsciScintilla.INDIC_HIDDEN, self.fold_ind)
        editor.setIndicatorForegroundColor(QColor(Qt.black), self.fold_ind)
        editor.setIndicatorHoverStyle(QsciScintilla.INDIC_COMPOSITIONTHICK, self.fold_ind)

        editor.indicatorClicked.connect(indicator_clicked)

    def styleText(self, start, end):
        text = self.parent().text()[start: end]
        editor = self.parent()
        self.startStyling(start)

        http = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        info_http = r'\d+?[.]\d+?[.]\d+?[.]\d+'
        info_time = r'\d+?-\d+?-\d+? \d+?:\d+?:\d+'  # 2022-11-01 11:21:54
        info_status = r'HTTP/1\.1 \d+'
        fold_info = r'run server fold at: .*'
        word = r'\w+|\s+|\W+'
        p = re.compile(
            fr'{http}|'
            fr'{info_http}|'
            fr'{info_time}|'
            fr'{info_status}|'
            fr'{fold_info}|'
            fr'{word}', re.I)
        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]
        total_length = start
        for i, token in enumerate(token_list):
            word, length = token
            if re.match(http, word, re.I):
                self.setStyling(length, self.styles_class.http)
                editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, self.url_ind)
                editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, total_length, length)

            elif re.match(info_http, word, re.I):
                self.setStyling(length, self.styles_class.info_http)
            elif re.match(info_time, word, re.I):
                self.setStyling(length, self.styles_class.info_time)
            elif re.match(info_status, word, re.I):
                with suppress(Exception):
                    match = re.match(r'(HTTP/1.1 )(\d+)', word, re.I)
                    l1 = match.span(1)[1] - match.span(1)[0]
                    self.setStyling(l1, self.styles_class.normal)
                    l2 = match.span(2)[1] - match.span(2)[0]
                    self.setStyling(l2, self.styles_class.info_status)

            elif re.match(fold_info, word, re.I):
                with suppress(Exception):
                    match = re.match(r'(run server fold at: )(.*)', word, re.I)
                    l1 = match.span(1)[1] - match.span(1)[0]
                    self.setStyling(l1, self.styles_class.normal)
                    l2 = match.span(2)[1] - match.span(2)[0]
                    self.setStyling(l2, self.styles_class.fold_info)
                    editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, self.fold_ind)
                    editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, total_length + l1, l2)
            else:
                self.setStyling(length, self.styles_class.normal)

            total_length += length


class WebServerConsole(QsciScintillaCompat):
    def __init__(self, parent):
        super(WebServerConsole, self).__init__(parent)
        self.setLexer(WebServerConsoleLexer(self))
        self.setReadOnly(True)
        self.setMargins(0)
        self.setUtf8(True)

        # 设置光标宽度, 颜色
        self.setCaretWidth(2)
        self.setCaretForegroundColor(QColor(Qt.red))

        # 设置选中颜色
        self.setSelectionBackgroundColor(QColor('#343544'))
        self.setSelectionForegroundColor(QColor('#D6D6D9'))

        # 匹配括号
        self.setBraceMatching(True)
        # self.setMatchedBraceForegroundColor(QColor('orange'))
        # self.setMatchedBraceBackgroundColor(QColor('yellow'))

        self.setStyleSheet('border:none')
