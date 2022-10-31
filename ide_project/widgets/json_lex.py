# -*- coding: utf-8 -*-
# @Time    : 2022/3/4 16:45
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : python_lex.py
# @Software: PyCharm

import json
import logging
import re


from logging import Handler

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QCursor, QColor, QFont, QImage
from PyQt5.Qsci import QsciLexerJSON, QsciLexerCustom
from PyQt5.QtWidgets import QApplication, QMenu

from customwidgets import Message
from .base_lex import BaseCodeWidget, Lexers, Themes
from qss.styles import MenuStyles


class MyLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(MyLexer, self).__init__(parent)
        # Default text settings
        # ----------------------
        self.setDefaultColor(QColor("#ff000000"))
        self.setDefaultPaper(QColor("#ffffffff"))
        self.setDefaultFont(QFont("Consolas", 14))

        # Initialize colors per style
        # ----------------------------
        self.setColor(QColor("#ff000000"), 0)  # Style 0: black
        self.setColor(QColor("#ff7f0000"), 1)  # Style 1: red
        self.setColor(QColor("#ff0000bf"), 2)  # Style 2: blue
        self.setColor(QColor("#ff007f00"), 3)  # Style 3: green

        # Initialize paper colors per style
        # ----------------------------------
        self.setPaper(QColor("#ffffffff"), 0)  # Style 0: white
        self.setPaper(QColor("#ffffffff"), 1)  # Style 1: white
        self.setPaper(QColor("#ffffffff"), 2)  # Style 2: white
        self.setPaper(QColor("#ffffffff"), 3)  # Style 3: white

        # Initialize fonts per style
        # ---------------------------
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 0)  # Style 0: Consolas 14pt
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 1)  # Style 1: Consolas 14pt
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 2)  # Style 2: Consolas 14pt
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 3)  # Style 3: Consolas 14pt

    def language(self):
        return "SimpleLanguage"

    def description(self, style):
        if style == 0:
            return "myStyle_0"
        elif style == 1:
            return "myStyle_1"
        elif style == 2:
            return "myStyle_2"
        elif style == 3:
            return "myStyle_3"
        ###
        return ""

    def styleText(self, start, end):
        # 1. Initialize the styling procedure
        # ------------------------------------
        self.startStyling(start)

        # 2. Slice out a part from the text
        # ----------------------------------
        text = self.parent().text()[start:end]

        # 3. Tokenize the text
        # ---------------------
        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len)
        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

        # 4. Style the text
        # ------------------
        # 4.1 Check if multiline comment
        multiline_comm_flag = False
        editor = self.parent()
        if start > 0:
            previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
            if previous_style_nr == 3:
                multiline_comm_flag = True
        # 4.2 Style the text in a loop
        for i, token in enumerate(token_list):
            if multiline_comm_flag:
                self.setStyling(token[1], 3)
                if token[0] == "*/":
                    multiline_comm_flag = False
            else:
                if token[0] in ["for", "while", "return", "int", "include"]:
                    # Red style
                    self.setStyling(token[1], 1)
                elif token[0] in ["(", ")", "{", "}", "[", "]", "#"]:
                    # Blue style
                    self.setStyling(token[1], 2)
                elif token[0] == "/*":
                    multiline_comm_flag = True
                    self.setStyling(token[1], 3)
                else:
                    # Default style
                    self.setStyling(token[1], 0)


class CustomJsonLex(QsciLexerJSON):
    pass


def _delete_safe(obj, name):
    try:
        delattr(obj, name)
    except Exception:
        pass


class JsonCodeWidget(BaseCodeWidget, Handler):
    type = Lexers.json
    custom_menu = True
    actions = [('format_action', 'json格式化')]
    use_thread = True
    read_only = False
    margin_context_flag = True

    def after_init(self):
        self.logger = logging.getLogger('json_lex')
        formater = logging.Formatter('[%(asctime)s] %(message)s')
        self.setFormatter(formater)
        self.setLevel(logging.INFO)
        self.logger.addHandler(self)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.setWhitespaceBackgroundColor(Qt.white)
        self.setStyleSheet('JsonCodeWidget{border:0px solid white}')
        self.setHotspotUnderline(True)
        self.setMouseTracking(True)
        # Handler.__init__(self, 0)

    def set_lexer(self):
        json_lex = QsciLexerJSON()
        json_lex.setColor(Qt.black, QsciLexerJSON.Error)
        json_lex.setPaper(Qt.white, QsciLexerJSON.Error)
        return json_lex
        # return MyLexer(self)

    def set_menu_policy(self, menu):
        act2 = menu.addAction('复制')
        act4 = menu.addAction('清空')
        act = menu.exec_(QCursor.pos())
        if act == act2:
            QApplication.clipboard().setText(self.selectedText())
        elif act == act4:
            self.clear()

    def set_format(self, selected_text: str, all_text: str, *a) -> str:
        try:
            data = json.loads(all_text)
            value = json.dumps(data, indent=4)
            return value
        except:
            pass

    def _margin_clicked_right(self, margin_nr, line_nr, state):
        marker_handler = self.markersAtLine(line_nr)
        if self.marker_is(marker_handler, self.marker_url):
            menu = QMenu()
            if self.theme == Themes.dark:
                menu.setStyleSheet(MenuStyles.dark)
            elif self.theme == Themes.light:
                menu.setStyleSheet(MenuStyles.light)
            action = menu.addAction('复制url')
            action1 = menu.addAction('复制请求体')
            action2 = menu.addAction('复制响应体')
            act = menu.exec_(QCursor.pos())
            flag = -1
            if act == action:
                flag = 0
            elif act == action1:
                flag = 1
            elif act == action2:
                flag = 2
            if flag >= 0:
                line = self.markerFindNext(line_nr + 1, 0b11)
                if line != -1:
                    print('this ', line_nr, line)
                    contents = (self.text(i) for i in range(line_nr, line + 1))
                    content = ''.join(contents)
                    self._parse_response(content, flag)
                else:
                    lines_count = self.lines()
                    print(line_nr, lines_count)
                    contents = (self.text(i) for i in range(line_nr, lines_count + 1))
                    content = ''.join(contents)
                    self._parse_response(content, flag)

    def _parse_response(self, content: str, flag):
        try:
            contents = content.splitlines()
            url = contents[0].split('post url: ')[-1].strip()
            data = contents[1].split('post data: ')[-1].strip()
            response = contents[3:] or []
            clip = QApplication.clipboard()
            if flag == 0:
                clip.setText(url)
                msg = '请求地址已复制'
            elif flag == 1:
                try:
                    py_data = eval(data)
                    clip.setText(json.dumps(py_data, ensure_ascii=False, indent=4))
                    msg = '请求体已复制'
                except:
                    pass
            elif flag == 2:
                clip.setText('\n'.join(response))
                msg = '响应体已复制'
            assert msg
            Message.info(msg, self)
        except:
            import traceback
            traceback.print_exc()

    def mousePressEvent(self, event):
        super(JsonCodeWidget, self).mousePressEvent(event)
        margin_width_x1 = self.marginWidth(0)
        margin_width = margin_width_x1 + self.marginWidth(1)
        position_x = event.x()
        if position_x <= margin_width:
            self.margin_context_flag = False
        else:
            self.margin_context_flag = True

    def set_default_custom_context_show(self) -> bool:
        return self.margin_context_flag

    # margin types
    margin_line = 0
    margin_symbol = 1

    # marker flags
    marker_url = 0
    marker_data = 1
    marker_resp = 2

    def marker_is(self, marker_handler: int, marker_flags: int) -> bool:
        return marker_handler == marker_flags + 1

    def set_markers(self):
        """
        :/new/debug.svg
        """
        symbol = QImage(':/new/运行，调试.svg').scaled(QSize(16, 16), transformMode=Qt.SmoothTransformation)
        self.setMarginType(1, self.SymbolMargin)
        self.setMarginWidth(1, 20)
        self.markerDefine(symbol, self.marker_url)
        self.markerDefine(self.Circle, self.marker_data)
        self.markerDefine(self.CircledPlus, self.marker_data)
        self.setMarginMarkerMask(1, 0b11)
        # self.markerAdd(0, 0)

        """
        self.append('base text\n')
        self.append('base text2\n')
        symbol = QsciScintilla.Circle
        symbol = QImage('exco_logo.png').scaled(QSize(16, 16), transformMode=Qt.SmoothTransformation)
        # self.setMarginType(1, QsciScintilla.SymbolMargin)
        # self.setMarginWidth(1, '000')
        self.setMarginType(1, self.SymbolMargin)
        self.setMarginWidth(1, 20)
        self.markerDefine(symbol, 0)
        self.markerDefine(self.Circle, 1)
        self.setMarginMarkerMask(1, 0b11)
        self.markerAdd(1, 0)
        self.markerAdd(0, 1)
        print('set marker', symbol)
        """

    #### logging handler ####
    def emit(self, record: 'LogRecord') -> None:
        try:
            url_tag = getattr(record, 'url_tag', False)
            data_tag = getattr(record, 'data_tag', False)
            resp_tag = getattr(record, 'resp_tag', False)
            _delete_safe(record, 'url_tag')
            _delete_safe(record, 'data_tag')
            _delete_safe(record, 'resp_tag')
            ret = self.format(record)
            self.append(ret + '\n')
            marker_lines = self.lines() - 2
            if url_tag:
                self.markerAdd(marker_lines, self.marker_url)
            if data_tag:
                pass
                # self.markerAdd(marker_lines, self.marker_data)
            if resp_tag:
                pass
                # self.markerAdd(marker_lines, self.marker_resp)
        except:
            import traceback
            traceback.print_exc()
