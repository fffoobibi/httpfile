import re

from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.qsci.custom_lexer import CustomStyles, CustomLexerCompat
from pyqt5utils.qsci.scintillacompat import QsciScintillaCompat
from widgets.signals import signal_manager
from widgets.styles import current_styles


class RunServerStyles(CustomStyles):
    normal = 1
    file_info = 2
    line_info = 3
    file_trace = 4

    @classmethod
    def defaultColor(cls, style):
        styles = current_styles.editor_run_console.get('color')
        if style == cls.normal:
            return QColor(styles['normal'])
        elif style == cls.file_info:
            return QColor(styles['file_info'])
        elif style == cls.line_info:
            return QColor(styles['line_info'])
        elif style == cls.file_trace:
            return QColor(styles['file_trace'])

    @classmethod
    def defaultPaper(cls, style):
        styles = current_styles.editor_run_console.get('paper')
        return QColor(styles['background'])

    @classmethod
    def defaultFont(cls, style, font: QFont):
        f = QFont('Consolas')
        f.setPointSize(font.pointSize())
        return f


class RunServerConsoleLexer(CustomLexerCompat):
    language_desc = 'python-run-server console'
    styles_class = RunServerStyles
    url_ind = 0
    fold_ind = 1
    file_trace_indic = 0

    def __init__(self, parent):
        super(RunServerConsoleLexer, self).__init__(parent)
        self.define_indicators(self.parent())

    def define_indicators(self, editor: 'RunServerConsole'):
        def indicator_clicked(line, index, keys):
            position = editor.positionFromLineIndex(line, index)
            if editor.hasIndicator(self.file_trace_indic, position):
                start = editor.getIndicatorStartPos(self.url_ind, position)
                end = editor.getIndicatorEndPos(self.url_ind, position)
                file_path = editor.text(start, end)
                line_value = editor.getIndicatorValue(self.file_trace_indic, position)
                signal_manager.emit(signal_manager.openFileAndMoveCursor, file_path, line_value, 0)

        colors = current_styles.editor_run_console['color']
        editor.indicatorDefine(QsciScintilla.INDIC_HIDDEN, self.file_trace_indic)
        editor.setIndicatorHoverStyle(QsciScintilla.INDIC_COMPOSITIONTHICK, self.file_trace_indic)
        editor.setIndicatorHoverForegroundColor(QColor(colors.get('file_info')))
        editor.indicatorClicked.connect(indicator_clicked)

    def styleText(self, start, end):
        text = self.parent().text()[start: end]
        editor: RunServerConsole = self.parent()
        self.startStyling(start)
        trace_back = r'File ".+", line \d+'
        word_pattern = r'\w+|\s+|\W+'
        p = re.compile(
            fr'{trace_back}|'
            fr'{word_pattern}', re.I)
        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]
        total_length = start
        for i, token in enumerate(token_list):
            word, length = token
            if re.match(trace_back, word, re.I):
                ret = re.match(r'(File ")(.+)(", line)(\s)(\d+)', word)
                l1 = ret.span(1)[1] - ret.span(1)[0]
                l2 = ret.span(2)[1] - ret.span(2)[0]
                l3 = ret.span(3)[1] - ret.span(3)[0]
                l4 = ret.span(4)[1] - ret.span(4)[0]
                l5 = ret.span(5)[1] - ret.span(5)[0]
                self.setStyling(l1, self.styles_class.file_trace)
                self.setStyling(l2, self.styles_class.file_info)
                self.setStyling(l3, self.styles_class.file_trace)
                self.setStyling(l4, self.styles_class.file_trace)
                self.setStyling(l5, self.styles_class.line_info)
                editor.setIndicatorByPositionLength(self.file_trace_indic, total_length + l1, l2, int(ret.group(5)) - 1)

            elif re.match(word_pattern, word, re.I):
                self.setStyling(length, self.styles_class.normal)
            else:
                self.setStyling(length, self.styles_class.normal)
            total_length += length


class RunServerConsole(QsciScintillaCompat):
    def __init__(self, parent):
        super(RunServerConsole, self).__init__(parent)
        self.setLexer(RunServerConsoleLexer(self))
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

        handler_color = current_styles.handler
        StylesHelper.set_v_history_style_dynamic(self, color=handler_color, background='transparent')
        StylesHelper.set_h_history_style_dynamic(self, color=handler_color, background='transparent')
