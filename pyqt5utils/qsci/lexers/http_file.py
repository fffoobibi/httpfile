import re
from typing import Dict

from PyQt5.Qsci import QsciScintilla, QsciAPIs
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

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


class HttpFileLexer(CustomLexerCompat):
    styles_class = HttpFileStyles
    language_desc = 'Http Files'
    url_indicator = 10

    def __init__(self, parent):
        super(HttpFileLexer, self).__init__(parent)
        editor = self.parent()
        print('editor ----', editor, parent)
        self.define_hotspots(editor)
        self.define_indicators(editor)
        self.define_apis(editor)

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

    def styleText(self, start, end):
        # 1. Initialize the styling procedure
        # ------------------------------------
        # self.startStyling(start)
        self.startStyling(0)

        # 2. Slice out a part from the text
        # ----------------------------------
        # text = self.parent().text()[start:end]
        text = self.parent().text()
        # 3. Tokenize the text
        # ---------------------
        editor = self.parent()

        splitter = r"^\s*?#.*?\s*?$"
        key_word = r"^\s*?post|get|delete|put|patch|head\s(?=http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\s*?$"
        http_path = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
        headers = r"^.*?\:.*?$"

        output2 = r'(?-s:^\s*?out)'
        output3 = r'^\s*?end\s+out\s*?$'
        output4 = r'.*?(?=end\s+out)\s*?'
        output_data = r'^\s*?(?<=out).*?(?=end\s+?out\s*?)'
        china = r'[\u4E00-\u9FA5]'
        p = re.compile(
            r'(?<=out).*?(?=end\s+?out\s*?)|'
            r'^\s*?out|'
            r'^\s*?end\s+out\s*?$|'
            r'(?<=out).*?|'
            r'.*?(?=end\s+?out)\s*?$|'

            r"^(?-s:\s*?#.*?\s*?$)|"
            r"^\s*?post|get|delete|put|patch|head\s(?=http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\s*?$|"
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\s*?$|"
            r"^(?-s:.*?\:.*?$)|"
            r"[\u4E00-\u9FA5]|"
            r"\s+|\w+",
            re.I | re.M | re.S)
        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

        total_length = 0
        for i, token in enumerate(token_list):
            word, length = token
            out_flag = False
            end_out_flag = False
            out_put_data_flag = False
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
                self.setStyling(length, self.styles_class.key)
                # Tell the editor which indicator-style to use
                # (pass it the indicator-style ID number)
                editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 9)
                # Assign a value to the text
                editor.SendScintilla(QsciScintilla.SCI_SETINDICATORVALUE, 666)
                # Now apply the indicator-style on the chosen text
                editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, total_length, len(word))

            elif re.match(http_path, word, re.IGNORECASE | re.MULTILINE):
                self.setStyling(length, self.styles_class.request_url)
                editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, self.url_indicator)
                editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, total_length, len(word))

            elif re.match(splitter, word, re.IGNORECASE | re.MULTILINE):
                self.setStyling(length, self.styles_class.splitter)
            elif re.match(headers, word, re.IGNORECASE | re.MULTILINE):
                headers_key, headers_value = word.split(':')
                self.setStyling(len(headers_key), self.styles_class.header)
                self.setStyling(1, self.styles_class.black)
                self.setStyling(len(headers_value), self.styles_class.black)
            else:
                self.setStyling(length, self.styles_class.response)

            line, col = editor.lineIndexFromPosition(total_length)
            if out_flag:
                level = editor.SendScintilla(editor.SCI_GETFOLDLEVEL, line)
                # print('get level', level)
                editor.SendScintilla(editor.SCI_SETFOLDLEVEL, line, 0 | QsciScintilla.SC_FOLDLEVELHEADERFLAG)
            elif end_out_flag:
                # print('rend end', line, col)
                editor.SendScintilla(editor.SCI_SETFOLDLEVEL, line, 0 | QsciScintilla.SC_FOLDLEVELHEADERFLAG)
            elif out_put_data_flag:
                level = editor.SendScintilla(editor.SCI_GETFOLDLEVEL, line)
                if level != 1 | QsciScintilla.SC_FOLDLEVELHEADERFLAG:
                    editor.SendScintilla(editor.SCI_SETFOLDLEVEL, line, 1 | QsciScintilla.SC_FOLDLEVELHEADERFLAG)

            total_length += length
