import keyword
import pathlib
import subprocess
import tempfile
from contextlib import suppress
from enum import IntEnum, Enum
from typing import List, Any, Tuple

from PyQt5.Qsci import QsciAPIs, QsciScintilla, QsciCommand
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDir, QThread, QFile
from PyQt5.QtGui import QColor, QFont, QKeySequence
from PyQt5.QtWidgets import QAction, QMenu

from pyqt5utils.workers import BackgroundWorker
from pyqt5utils.qsci.scintillacompat import QsciScintillaCompat


class ColorTypes(str, Enum):
    code_background = 'code_background',

    margin_foreground = 'margin_foreground',
    margin_background = 'margin_background',

    guides_foreground = 'guides_foreground',
    guides_background = 'guides_background',

    caret_foreground = 'caret_foreground',
    caretline_background = 'caretline_background',

    matchedbrace_foreground = 'matchedbrace_foreground',
    matchedbrace_background = 'matchedbrace_background',

    foldmargin_backgrounds = 'foldmargin_backgrounds',

    selection_foreground = 'selection_foreground',
    selection_background = 'selection_background'


class Themes(IntEnum):
    none = -1
    dark = 0
    light = 1

    @classmethod
    def dark_theme(cls) -> dict:
        return dict(
            code_background='#1B1A19',
            margin_foreground='#4D4C40',
            margin_background='#2D2B29',
            guides_foreground='#4F4E4E',
            guides_background=None,
            caret_foreground='#FFB900',
            caretline_background='#212131',
            matchedbrace_foreground='#37AAEB',
            matchedbrace_background='#3B514D',
            foldmargin_backgrounds=['#2D2B29', '#2D2B29'],
            selection_foreground=None,
            selection_background='#323341'
        )

    def light_theme(self):
        pass

    def theme_color(self, color_type: ColorTypes):
        pass


class Lexers(IntEnum):
    none = -1
    python = 0
    javascript = 1
    json = 2
    text = 3
    html = 4
    markdown = 5


class CodeState(IntEnum):
    normal = 0
    read_only = 1
    multi_line = 2
    macro = 3


class RepeatKey(IntEnum):
    key_none = -1
    key_ctrl = 0


class MenuStyles(str):
    none = ''
    dark = '''
            QMenu{background: #333231;border:1px solid #434241}
            QMenu::item{
              padding:3px 20px;
              color:lightgray;
              font-size:9pt;
              font-family:微软雅黑}
            QMenu::item:hover{
              background-color:#242220;
            }
            QMenu::item:selected{
              background-color:#242220;
            }'''
    light = '''
            QMenu{background: #EEE9E9;border:1px solid white}
            QMenu::item{
              padding:3px 20px;
              color:black;
              font-size:9pt;
              font-family:微软雅黑}
            QMenu::item:hover{
              background-color:lightgray;
            }
            QMenu::item:selected{
              background-color:gray;
            }'''


class BaseCodeWidget(QsciScintillaCompat):
    """
    https://qscintilla.com/
    """
    cursor_signal = pyqtSignal(int, int)
    key2_signal = pyqtSignal(int)
    click_signal = pyqtSignal()

    custom_menu: bool = False
    use_thread: bool = False
    read_only: bool = False

    type: Lexers = Lexers.none

    actions = [('format_action', '格式化代码')]

    attrs = {
        Themes.dark: Themes.dark_theme()
    }

    word_indicator_show = False

    class _RunThread(QThread):

        signal = pyqtSignal(str)

        def __init__(self, cmd):
            super().__init__()
            self.cmd = cmd

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

    def after_init(self):
        pass

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        if cls.__dict__.get('attrs', None) is not None:
            for theme_type in cls.attrs:
                cls.attrs[theme_type].update(BaseCodeWidget.attrs.get(theme_type, {}))

    def __init__(self, theme: Themes = Themes.light,
                 worker: BackgroundWorker = None):
        super().__init__()
        self.theme = theme
        # set worker
        if self.use_thread:
            self._worker = worker or BackgroundWorker()
        else:
            self._worker = worker

        self.run_content: List[str] = []

        self._repeat_timer = QTimer(self)
        self._repeat_timer.timeout.connect(self._repeat_timeout)
        self._repeat_count = 0
        self._repeat_key = None
        self._code_state = CodeState.normal
        self.key2_signal.connect(lambda v: print('two '))
        self.click_signal.connect(self._click)
        self._current_line = -1
        self._current_col = -1
        self._indicator_word_start = -1
        self._indicator_word_length = -1

        # 右鍵事件
        if self.custom_menu:
            def _process():
                if self.set_default_custom_context_show():
                    menu = QMenu()
                    if self.theme == Themes.dark:
                        menu.setStyleSheet(MenuStyles.dark)
                    elif self.theme == Themes.light:
                        menu.setStyleSheet(MenuStyles.light)
                    self.context_menu = menu
                    self.set_menu_policy(menu)

            self.context_menu = self._create_dft_context_menu()
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(_process)
        else:
            self.context_menu = None

        self.set_base_style()
        self.set_commands()
        self.set_indicators()
        self.set_markers()
        self.set_slots()

        self._inter = self.set_lexer()
        if self._inter:
            self._apis = QsciAPIs(self._inter)
            for api in self.set_apis():
                self._apis.add(api)
            self._apis.prepare()
            self._inter.setAPIs(self._apis)
            self.setLexer(self._inter)

        self.set_them(self.theme)

        self.setReadOnly(self.read_only)
        self.after_init()

    def set_font(self) -> QFont:
        """设置字体"""
        return None

    def set_lexer(self) -> Any:
        """设置词法分析"""
        return None

    def set_apis(self) -> List[str]:
        """设置代码提示"""
        return []

    def set_commands(self):
        """设置快捷键功能"""

        def copy_line():
            if not self.isReadOnly():
                if not self.hasSelectedText():
                    self.SendScintilla(QsciCommand.LineCopy)
                else:
                    self.copy()

        def comment_line():
            def _comment_line(line_content: str, line: int):
                if not line_content.strip().startswith('#'):
                    for index, c in enumerate(line_content):
                        if c:
                            self.insertAt('#', line, index)
                            break
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

        def format_file():
            self.format_code()

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
        """设置主题"""
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

    def set_base_style(self):
        """设置基本样式"""
        self.setEolMode(self.SC_EOL_LF)  # 以\n换行
        self.setWrapMode(self.WrapNone)  # 自动换行。self.WrapWord是父类QsciScintilla的
        self.setAutoCompletionSource(self.AcsAll)  # 自动补全。对于所有Ascii字符
        self.setAutoCompletionCaseSensitivity(False)  # 自动补全大小写敏感
        self.setAutoCompletionThreshold(1)  # 输入多少个字符才弹出补全提示
        self.setFolding(self.BoxedTreeFoldStyle)  # 代码可折叠
        self.setFont(self.set_font() or QFont('微软雅黑', 10))  # 设置默认字体
        self.setTabWidth(4)
        self.setTabletTracking(True)
        self.setTabIndents(True)

        # 边栏字体
        self._margin_font = QFont('Consolas', 10)
        self.setMarginsFont(self._margin_font)

        # 行号显示
        self.setMarginType(0, self.NumberMargin)  # 0~4。第0个左边栏显示行号
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, '00')  # 边栏宽度
        # self.setMarginsBackgroundColor(QColor('#2D2B29'))  # 边栏背景颜色

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
        if self.theme == Themes.light:
            self.setCaretForegroundColor(QColor('#FFB900'))
            self.setCaretLineBackgroundColor(QColor('#E8E8FF'))

        # 折叠栏
        # self.setFoldMarginColors(QColor('#2D2B29'), QColor('#2D2B29'))

        # 括号
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        # self.setMatchedBraceForegroundColor(QColor('#37AAEB'))
        # self.setMatchedBraceBackgroundColor(QColor('#3B514D'))

        # 字体选中颜色
        # self.setSelectionBackgroundColor(QColor('#343544'))

        # 信号
        self.linesChanged.connect(self.set_line_width_slot)
        self.cursorPositionChanged.connect(self._cursor_change)

    def set_indicators(self):
        """设置indicator"""
        self.indicatorDefine(self.BoxIndicator, 10)
        self.setIndicatorForegroundColor(QColor('#00D5F5'), 10)

    def set_markers(self):
        pass

    def set_slots(self):
        self.setMarginSensitivity(1, True)
        self.marginClicked.connect(self._margin_clicked)
        self.marginRightClicked.connect(self._margin_clicked_right)

    def set_default_custom_context_show(self) -> bool:
        return True

    @property
    def current_line_col(self) -> Tuple:
        pos = self.currentPosition()
        return self.lineIndexFromPosition(pos)

    def _margin_clicked(self, margin_nr, line_nr, state):
        pass

    def _margin_clicked_right(self, margin_nr, line_nr, state):
        pass

    def _create_dft_context_menu(self) -> QMenu:
        menu = QMenu()
        if self.theme == Themes.dark:
            menu.setStyleSheet(MenuStyles.dark)
        for act_name, text in self.actions:
            # ge_act = menu.addAction(text)
            ge_act = QAction(text)
            setattr(self, act_name, ge_act)
        return menu

    def set_menu_policy(self, menu: QMenu) -> None:
        pass

    def _cursor_change(self, line, col):
        self._current_line = line
        self._current_col = col
        self.cursor_signal.emit(line, col)

    def set_line_width_slot(self):
        count = len(str(self.lines()))
        self.setMarginWidth(0, '0' * count + '00')

    def _run(self, cmd):
        self.run_content.clear()
        self._run_thread = self._RunThread(cmd)  # self.output, self)
        self._run_thread.signal.connect(self.run_content.append)
        self._run_thread.start()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.click_signal.emit()

    # def keyReleaseEvent(self, event):
    #
    #     if event.key() == Qt.Key_Control:
    #         self._repeat_key = Qt.Key_Control
    #         if not self._repeat_timer.isActive():
    #             self._repeat_timer.start(400)
    #         self._repeat_count += 1
    #         if self._repeat_count == 2:
    #             self._repeat_timer.stop()
    #             self._repeat_count = 0
    #             self.key2_signal.emit(Qt.Key_Control)
    #             self._code_state = CodeState.multi_line
    #     else:
    #         self._repeat_key = None
    #         self._code_state = CodeState.normal
    #
    #     # if event.modifiers() & Qt.Key_Control and event.key() == Qt.Key_X:
    #     #     print('ctrl+x ---')
    #     # else:
    #     #     pass
    #     super().keyReleaseEvent(event)

    def _repeat_timeout(self):
        if self._repeat_key == Qt.Key_Control:
            self._repeat_count = 0
            self._repeat_timer.stop()

    def _click(self):
        if self.word_indicator_show:
            line, col = self.getCursorPosition()
            word = self.wordAtLineIndex(line, col)
            # clear indicator
            self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 10)
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, self._indicator_word_start,
                               self._indicator_word_length)
            if word:
                # add indicator
                word_index = self.positionFromLineIndex(line, col)
                start = self.SendScintilla(self.SCI_WORDSTARTPOSITION, word_index, 1)
                end = self.SendScintilla(self.SCI_WORDENDPOSITION, word_index, 1)
                self._indicator_word_start = start
                self._indicator_word_length = len(word)
                line_content = self.text(line)
                if_comment = True if line_content.strip().startswith('#') else False
                if not word.isnumeric() and word not in keyword.kwlist and not if_comment:
                    self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 10)
                    self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start, self._indicator_word_length)

    def set_format(self, selected_text: str, all_text: str, *a, **kw) -> str:
        return all_text

    # 格式化代码
    def format_code(self, *a, **kw):
        def _ok(format_text):
            self.setText(format_text)

        def _error(err):
            pass

        all_text = self.text()
        selected_text = self.selectedText()
        self.add_task(self.set_format,
                      args=(selected_text, all_text, *a),
                      kws=kw, call_back=_ok, err_back=_error)

    ############ task ###########
    def add_task(self, fn, args=(), kws={}, call_back=None, err_back=None) -> bool:
        if self._worker:
            self._worker.add_task(fn, args, kws, call_back, err_back)
            return True
        return False

    def add_coro(self, coro, call_back=None, err_back=None) -> bool:
        if self._worker:
            self._worker.add_coro(coro, call_back, err_back)
            return True
        return False

    ### load file ###
    def load_file(self, file_path):
        with suppress(Exception):
            # method1
            import mmap
            with open(file_path, 'r+b') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    contents = mm.read()
                    self.setText(contents.decode('utf-8'))

            # method2
            # file = QFile(file_path)
            # if not file.open(QFile.ReadOnly | QFile.Unbuffered):
            #     return
            # self.read(file)
            # file.close()

            # from pathlib import Path
            # self.setText(Path(file_path).read_text(encoding='utf-8'))
            # return self.lines()

    def load_content(self, content: str):
        self.setText(content)
        # return len(content.splitlines())
