import re
from typing import Dict

from PyQt5.Qsci import QsciScintilla, QsciAPIs
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPixmap
from cached_property import cached_property

from pyqt5utils.qsci.base import QsciScintillaCompat
from pyqt5utils.qsci.custom_lexer import CustomStyles, CustomLexerCompat


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
    request_data = 14
    variable = 15

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
        elif style == cls.request_data:
            return QColor(Qt.darkYellow)
        elif style == cls.dynamic_variable:
            return QColor(Qt.darkGreen)

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


class HttpFileLexer(CustomLexerCompat):
    styles_class = HttpFileStyles
    language_desc = 'Http Files'
    url_indicator = 10

    run_margin_type = 1
    run_margin_pixmap = ':/icon/运行，调试.svg'

    header_fold_level = 5

    _load_file = False

    def __init__(self, parent):
        super(HttpFileLexer, self).__init__(parent)
        editor = self.parent()
        self.runner = HttpRunner(editor, self)
        self.define_hotspots(editor)
        self.define_indicators(editor)
        self.define_apis(editor)
        self.define_markers(editor)

    def margin_slot(self, margin_lr, line, state):
        # from PyQt5 import QsciScintilla
        editor: QsciScintilla = self.parent()
        margin_type = editor.markersAtLine(line)
        if margin_type == self.run_margin_type + 1:
            try:
                editor.run_margin_signal.emit(line)
            except:
                pass
            # self.runner.run_current_http(line)
        position = editor.positionFromLineIndex(line, 0)
        style = editor.styleAt(position)
        print('style: ', style)

    def define_markers(self, editor: QsciScintilla):
        # from PyQt5 import QsciScintilla
        editor.setMarginType(self.run_margin_type, editor.SymbolMargin)
        editor.markerDefine(QPixmap(self.run_margin_pixmap).scaled(16, 16, transformMode=Qt.SmoothTransformation),
                            self.run_margin_type)
        editor.setMarginWidth(self.run_margin_type, 24)
        editor.setMarginSensitivity(self.run_margin_type, True)
        editor.marginClicked.connect(self.margin_slot)
        # editor.marginRightClicked.connect(self.margin_slot)
        # editor.markerDefine(editor.SymbolMargin, self.run_margin)

    def define_apis(self, editor):
        api = QsciAPIs(self)
        autocompletions = [
            "variable_one",  # Used for Autocompletion only
            "variable_two",  # Used for Autocompletion only
            "function_one(int arg_1)",  # Name used for Autocompletion, args for Call tips
            "function_two(float arg_1)"  # Name used for Autocompletion, args for Call tips
        ]
        for ac in autocompletions:
            api.add(ac)
        self.setAPIs(api)

    def define_hotspots(self, editor):
        pass
        # editor.SendScintilla(editor.SCI_STYLESETHOTSPOT, self.styles_class.request_url, True)
        # editor.setHotspotForegroundColor(QColor(Qt.blue))
        # editor.SCN_HOTSPOTCLICK.connect(self.hotpot_func)

    def define_indicators(self, editor):
        def indicator_clicked(line, index, keys):
            # Retrieve absolute position
            position = editor.positionFromLineIndex(line, index)
            # Retrieve given value
            value = editor.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT,
                                         indicator_num, position)

            start = editor.SendScintilla(QsciScintilla.SCI_INDICATORSTART, indicator_num, position)
            end = editor.SendScintilla(QsciScintilla.SCI_INDICATOREND, indicator_num, position)
            # print('start: ', start, 'end: ', end)
            # print('indicator text: ', editor.text(start, end))
            # print("indicator clicked in line '{}',index'{}', value'{}'".format(line, index, value))

        indicator_num = 9
        # editor.indicatorDefine(indicator_num, QsciScintilla.SquigglePixmapIndicator, Qt.red)
        editor.indicatorDefine(QsciScintilla.INDIC_HIDDEN, indicator_num)  # 波浪线
        editor.setIndicatorHoverStyle(QsciScintilla.INDIC_FULLBOX, indicator_num)

        editor.indicatorDefine(QsciScintilla.INDIC_HIDDEN, self.url_indicator)
        editor.setIndicatorForegroundColor(QColor(Qt.blue), self.url_indicator)
        editor.setIndicatorHoverStyle(QsciScintilla.INDIC_COMPOSITIONTHICK, self.url_indicator)
        editor.setIndicatorHoverForegroundColor(QColor(Qt.blue), self.url_indicator)
        editor.setIndicatorDrawUnder(False, self.url_indicator)

        editor.indicatorClicked.connect(indicator_clicked)

    def hotpot_func(self, position, modifiers):
        print("Hotspot clicked at position: " + str(position))

    @cached_property
    def url_indicators(self):
        return []

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.parent().text()[start: end]
        editor = self.parent()
        splitter = r"^\s*?#.*?\s*?$"
        key_word = r"post|get|delete|put|patch|head\s(?=http[s]?://.*?$)\s*?$"
        # http_path = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
        http_path = r'http[s]?://.*?$'
        headers = r"^.*?\:.*?$"

        output2 = r'(?-s:^\s*?out)'
        output3 = r'^\s*?end\s+out\s*?$'
        output4 = r'.*?(?=end\s+out)\s*?'
        output_data = r'^\s*?(?<=out).*?(?=end\s+?out\s*?)'
        china = r'[\u4E00-\u9FA5]'
        variable = r'{{\S*?}}'
        p = re.compile(
            r'(?<=out).*?(?=end\s+?out\s*?)|'
            r'^\s*?out|'
            r'^\s*?end\s+out\s*?$|'
            r'(?<=out).*?|'
            r'.*?(?=end\s+?out)\s*?$|'
            r"^(?-s:\s*?#.*?\s*?$)|"
            r"post|get|delete|put|patch|head\s(?=http[s]?://.*?)$|"
            fr'{http_path}|'
            r"^(?-s:.*?\:.*?$)|"
            r"[\u4E00-\u9FA5]|"
            r"\s+|\w+",
            re.I | re.M | re.S)
        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]
        total_length = start
        for i, token in enumerate(token_list):
            word, length = token
            out_flag = False
            end_out_flag = False
            out_put_data_flag = False
            line, col = editor.lineIndexFromPosition(total_length)

            if re.match(output_data, word, re.I | re.M | re.S):
                self.setStyling(length, self.styles_class.bold)
                out_put_data_flag = True
            elif re.match(output2, word, re.I | re.M | re.S):
                line, col = editor.lineIndexFromPosition(total_length)
                out_flag = True
                self.setStyling(length, self.styles_class.output)
            elif re.match(output3, word, re.I | re.M | re.S):
                end_out_flag = True
                self.setStyling(length, self.styles_class.output)
            elif re.match(output4, word, re.I | re.M | re.S):
                self.setStyling(length, self.styles_class.output)
            elif re.match(china, word):
                self.setStyling(length, self.styles_class.chinese)
            elif re.match(key_word, word, re.IGNORECASE | re.MULTILINE):
                # from PyQt5 import QsciScintilla
                line, col = editor.lineIndexFromPosition(total_length)
                # print('find line ,', line)
                # print('---')
                editor: QsciScintilla
                editor.markerDelete(line, self.run_margin_type)
                editor.markerAdd(line, self.run_margin_type)
                self.setStyling(length, self.styles_class.key)
                editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 9)
                editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, total_length, len(word))
                # self.url_indicators.append((line, col, total_length, editor.text(line)))

            elif re.match(http_path, word, re.IGNORECASE | re.MULTILINE):
                ret = re.findall('(.*?)({{)(.*?)(}})(.*)', word)
                if ret:
                    a0, a1, a2, a3, a4 = ret[0]
                    try:
                        print(self.styles_class.__members__.keys())
                        self.setStyling(len(a0), self.styles_class.request_url)
                        self.setStyling(len(a1), self.styles_class.variable)
                        self.setStyling(len(a2), self.styles_class.variable)
                        self.setStyling(len(a3), self.styles_class.variable)
                        self.setStyling(len(a4), self.styles_class.request_url)
                    except:
                        import traceback
                        traceback.print_exc()
                else:
                    self.setStyling(length, self.styles_class.request_url)

                editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, self.url_indicator)
                value = editor.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT, self.url_indicator,
                                             total_length - 1)
                if not value:
                    editor.SendScintilla(QsciScintilla.SCI_SETINDICATORVALUE, line + 1)
                editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, total_length, len(word))


            elif re.match(splitter, word, re.IGNORECASE | re.MULTILINE):
                self.setStyling(length, self.styles_class.splitter)
            elif re.match(headers, word, re.IGNORECASE | re.MULTILINE):
                try:
                    # line, col = editor.lineIndexFromPosition(total_length)
                    # editor.SendScintilla(editor.SCI_SETFOLDLEVEL, line, 5 | QsciScintilla.SC_FOLDLEVELHEADERFLAG)
                    headers_key, headers_value = word.split(':')
                    self.setStyling(len(headers_key), self.styles_class.header)
                    self.setStyling(1, self.styles_class.black)
                    self.setStyling(len(headers_value), self.styles_class.black)
                except:
                    pass
            else:
                self.setStyling(length, self.styles_class.response)

            if out_flag:
                level = editor.SendScintilla(editor.SCI_GETFOLDLEVEL, line)
                editor.SendScintilla(editor.SCI_SETFOLDLEVEL, line, 0 | QsciScintilla.SC_FOLDLEVELHEADERFLAG)
            elif end_out_flag:
                editor.SendScintilla(editor.SCI_SETFOLDLEVEL, line, 0 | QsciScintilla.SC_FOLDLEVELHEADERFLAG)
            elif out_put_data_flag:
                level = editor.SendScintilla(editor.SCI_GETFOLDLEVEL, line)
                if level != 1 | QsciScintilla.SC_FOLDLEVELHEADERFLAG:
                    editor.SendScintilla(editor.SCI_SETFOLDLEVEL, line, 1 | QsciScintilla.SC_FOLDLEVELHEADERFLAG)

            total_length += length

        try:
            editor.file_styled.emit()
        except:
            pass


class HttpRunner(object):
    def __init__(self, editor: QsciScintillaCompat, lexer: HttpFileLexer):
        self.editor = editor
        self.lexer = lexer

    def _find_url_method(self, line):
        position = self.editor.lineEndPosition(line)
        url = self.editor.getIndicatorText(self.lexer.url_indicator, position - 1)
        method = self.editor.text(line).strip()
        ret = re.findall(r'(get|post|patch|delete|put|header|options)(\s+?)(http[s]?://)', method, re.IGNORECASE)
        if ret:
            return url, ret[0][0].lower()
        return url, ''

    def _find_data(self, line):
        pass

    def _find_headers(self, line: int) -> dict:
        start_line = line
        headers = ''
        while True:
            start_line += 1
            start_position = self.editor.positionFromLineIndex(start_line, 0)
            if self.editor.styleAt(start_position) in [HttpFileStyles.header, HttpFileStyles.response]:
                headers += self.editor.text(start_line)
            else:
                break
        headers = headers.strip()
        ret = {}
        for line_content in headers.splitlines():
            line_content: str
            try:
                key, value = line_content.split(':', 1)
                ret[key.strip()] = value.strip()
            except:
                pass
        return ret

    def run_current_http(self, line):
        # from PyQt5 import QsciScintilla
        # self.editor: QsciScintilla

        url, method = self._find_url_method(line)
        headers = self._find_headers(line)
        print(url, method)
        style = self.editor.styleAt(line)
        print(style == HttpFileStyles.request_url, style)
        headers = self._find_headers(line)
        # self.editor.getSubStyleRange()
        print(headers)
