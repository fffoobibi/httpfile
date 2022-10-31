# -*- coding: utf-8 -*-
# @Time    : 2022/3/8 8:24
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : base_coder.py
# @Software: PyCharm
import tempfile
import subprocess
import pathlib

from typing import List, Any

from PyQt5.Qsci import QsciAPIs, QsciScintilla, QsciCommand
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFontMetrics, QFont, QKeySequence

from enum import IntEnum

from PyQt5.QtWidgets import QWidget, QTextBrowser, QAction

from config import AppConfig
from qss.styles import Theme


class Lexers(IntEnum):
    none = -1
    python = 0
    javascript = 1
    json = 2
    text = 3
    html = 4


class BaseCodeWidget(QsciScintilla):
    cursor_signal = pyqtSignal(int, int)

    type = Lexers.none

    attrs = {
        Themes.dark: dict(
            code_background='#1B1A19',

            margin_foreground='lightgray',
            margin_background='#2D2B29',

            guides_foreground='#4F4E4E',
            guides_background=None,

            caret_foreground='#FFB900',
            caretline_background='#212131',

            matchedbrace_foreground='#37AAEB',
            matchedbrace_background='#3B514D',

            foldmargin_backgrounds=['#2D2B29', '#2D2B29'],

            selection_foreground=None,
            selection_background='#323341'),
    }

    def __init_subclass__(cls, **kwargs):
        if cls.__dict__.get('attrs', None) is not None:
            for theme_type in cls.attrs:
                cls.attrs[theme_type].update(BaseCodeWidget.attrs.get(theme_type, {}))

    class _RunThread(QThread):

        signal = pyqtSignal(str)

        def __init__(self, cmd, write_to: QTextBrowser, code_widget):
            super().__init__()
            self.cmd = cmd
            self.output = write_to
            self.code_widget = code_widget
            self.signal.connect(self.write_msg)

        def write_msg(self, msg: str):
            self.output.append(msg)
            self.code_widget.run_content.append(msg)

        def run(self) -> None:
            popen = subprocess.Popen(self.cmd, shell=True,
                                     stdout=subprocess.PIPE,
                                     stdin=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
            self.signal.emit(self.cmd + '\n')
            while True:
                msg = popen.stdout.readline()
                if msg == b'':
                    break
                self.signal.emit(msg.decode('utf8').strip())
            popen.wait()
            self.signal.emit(f'\n进程已结束,退出代码 {popen.returncode}')

    def set_font(self) -> QFont:
        return None

    def set_lexer(self) -> Any:
        return None

    def set_apis(self) -> List[str]:
        return []

    def set_commands(self):
        def copy_line():
            if not self.isReadOnly():
                if not self.hasSelectedText():
                    self.SendScintilla(QsciCommand.LineCopy)
                else:
                    self.copy()

        def comment_line():
            def _comment_line(line_content: str, line: int):
                if not line_content.strip().startswith('#'):
                    self.insertAt('#', line, 0)
                else:
                    line_start = self.positionFromLineIndex(line, 0)
                    for index, c in enumerate(line_content):
                        if c == '#':
                            self.SendScintilla(self.SCI_DELETERANGE, line_start + index, 1)
                            break
            if not self.isReadOnly():
                if not self.hasSelectedText():
                    line, col = self.getCursorPosition()
                    line_content = self.text(line)
                    if len(line_content) > 0:
                        _comment_line(line_content, line)
                else:
                    l1, c1, l2, c2 = self.getSelection()
                    if l1 != -1 and l2 != -1:
                        for i in range(l1, l2 + 1):
                            line_content = self.text(i)
                            if len(line_content) > 0:
                                _comment_line(line_content, i)

        commands = self.standardCommands()
        commands_list = [(Qt.ControlModifier | Qt.Key_C, copy_line),
                         (Qt.ControlModifier | Qt.Key_Slash, comment_line)]
        for key, func in commands_list:
            command = commands.boundTo(key)
            # clear the default
            if command is not None:
                command.setKey(0)
            # set command
            action = QAction(f'{func.__name__}', self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(func)
            self.addAction(action)

    def set_them(self, type: Themes):
        colors = self.attrs.get(type, None)
        if colors is not None:
            code_background = colors.get('code_background')
            if self._inter is None:
                self.setPaper(QColor(code_background)) if code_background else None

            else:
                self._inter.setPaper(QColor(code_background)) if code_background else None

            margin_foreground = colors.get('margin_foreground')
            margin_background = colors.get('margin_background')
            self.setMarginsForegroundColor(QColor(margin_foreground)) if margin_foreground else None
            self.setMarginsBackgroundColor(QColor(margin_background)) if margin_background else None

            guides_foreground = colors.get('guides_foreground')
            guides_background = colors.get('guides_background')
            self.setIndentationGuidesForegroundColor(QColor(guides_foreground)) if guides_foreground else None

            caret_foreground = colors.get('caret_foreground')
            caretline_background = colors.get('caretline_background')
            self.setCaretForegroundColor(QColor(caret_foreground)) if caret_foreground else None
            self.setCaretLineBackgroundColor(QColor(caretline_background)) if caretline_background else None

            matchedbrace_foreground = colors.get('matchedbrace_foreground')
            matchedbrace_background = colors.get('matchedbrace_background')
            self.setMatchedBraceForegroundColor(QColor(matchedbrace_foreground)) if matchedbrace_foreground else None
            self.setMatchedBraceBackgroundColor(QColor(matchedbrace_background)) if matchedbrace_background else None

            foldmargin_backgrounds = colors.get('foldmargin_backgrounds')
            self.setFoldMarginColors(
                *[QColor(color) for color in foldmargin_backgrounds]) if foldmargin_backgrounds else None

            selection_foreground = colors.get('selection_foreground')
            selection_background = colors.get('selection_background')
            self.setSelectionForegroundColor(QColor(selection_foreground)) if selection_foreground else None
            self.setSelectionBackgroundColor(QColor(selection_background)) if selection_background else None

    def set_run_cmd(self, file_name: str) -> str:
        return None

    def set_base_style(self):
        self.setEolMode(self.SC_EOL_LF)  # 以\n换行
        self.setWrapMode(self.WrapNone)  # 自动换行。self.WrapWord是父类QsciScintilla的
        self.setAutoCompletionSource(self.AcsAll)  # 自动补全。对于所有Ascii字符
        self.setAutoCompletionCaseSensitivity(False)  # 自动补全大小写敏感
        self.setAutoCompletionThreshold(1)  # 输入多少个字符才弹出补全提示
        self.setFolding(True)  # 代码可折叠
        self.setFont(self.set_font() or QFont('微软雅黑', 10))  # 设置默认字体
        self.setTabWidth(4)
        self.setTabletTracking(True)
        self.setTabIndents(True)

        # 边栏字体
        self._margin_font = QFont('Consolas', 9)
        self.setMarginsFont(self._margin_font)

        # 行号显示
        self.setMarginType(0, self.NumberMargin)  # 0~4。第0个左边栏显示行号
        self.setMarginLineNumbers(0, True)  # 我也不知道
        self.setMarginWidth(0, QFontMetrics(self._margin_font).width('0') + 5)  # 边栏宽度
        # self.setMarginsBackgroundColor(QColor('#2D2B29'))  # 边栏背景颜色

        # symbol
        self.setMarginType(1, self.SymbolMargin)
        self.setMarginWidth(1, 16)

        # self.setMarginsForegroundColor(Qt.lightGray)

        self.setAutoIndent(True)  # 换行后自动缩进, 括号自动补全
        self.setIndentationGuides(True)  # 设置虚线
        self.setBackspaceUnindents(True)
        self.setUtf8(True)  # 支持中文字符
        # self.setIndentationGuidesForegroundColor(QColor('#4F4E4E'))

        # 光标设置
        self.setCaretWidth(2)
        self.setCaretLineVisible(True)
        # self.setCaretForegroundColor(QColor('#FFB900'))
        # self.setCaretLineBackgroundColor(QColor('#212131'))

        # 折叠栏
        # self.setFoldMarginColors(QColor('#2D2B29'), QColor('#2D2B29'))

        # 括号
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        # self.setMatchedBraceForegroundColor(QColor('#37AAEB'))
        # self.setMatchedBraceBackgroundColor(QColor('#3B514D'))

        # 字体选中颜色
        # self.setSelectionBackgroundColor(QColor('#343544'))

        # 信号
        self.linesChanged.connect(self.set_line_width)
        self.cursorPositionChanged.connect(self._cursor_change)

    def _cursor_change(self, line, col):
        self.cursor_signal.emit(line, col)

    def __init__(self, file_name: str, theme: Themes, output: QWidget, raw_file: str = None,
                 config: AppConfig = None):
        super().__init__()
        self.file_name = file_name
        self.output = output
        self.theme = theme
        self.raw_file = raw_file
        self.config = config
        self.ide = None

        self.run_content: List[str] = []
        self._key_actions = []

        self.set_base_style()
        self.set_commands()

        self._inter = self.set_lexer()
        if self._inter:
            self._apis = QsciAPIs(self._inter)
            for api in self.set_apis():
                self._apis.add(api)
            self._apis.prepare()
            self._inter.setAPIs(self._apis)
            self.setLexer(self._inter)

        # self.set_base_style()
        self.set_them(self.theme)
        # self.set_commands()

        if raw_file is not None and pathlib.Path(raw_file).exists():
            content = pathlib.Path(raw_file).read_text(encoding='utf8')
            self.setText(content)

    def add_marker(self, margin_id, line, keys):
        mark = self.markersAtLine(line)
        if mark:
            self._run()
        else:
            self.markerAdd(line, 0)

    def set_line_width(self):
        count = len(str(self.lines()))
        self.setMarginWidth(0, QFontMetrics(self._margin_font).width('0' * count) + 5)

    def _run(self):
        file_ = pathlib.Path(tempfile.gettempdir()) / self.file_name
        file_.write_text(self.text(), encoding='utf8')
        cmd = self.set_run_cmd(file_)
        self.output.clear()
        self.run_content.clear()
        self._run_thread = self._RunThread(cmd, self.output, self)
        self._run_thread.start()
