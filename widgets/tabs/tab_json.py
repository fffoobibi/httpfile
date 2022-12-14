import json
import re
import subprocess
from typing import List

import jmespath
from PyQt5.Qsci import QsciLexerJSON
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent, QRectF, QSize
from PyQt5.QtGui import QColor, QIcon, QFontMetricsF, QFont, QCursor, QPainter, QPainterPath, QTextOption, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QTextEdit, QHBoxLayout, QPushButton, \
    QSpacerItem, QSizePolicy, QListWidget, QMenu, QApplication, QListWidgetItem
from cached_property import cached_property
from lsprotocol.types import ClientCapabilities

from lsp.interface import StdIoLanguageClient
from lsp.utils import LspContext
from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.qsci.scintillacompat import QsciScintillaCompat
from . import register, TabCodeWidget
from .utils import must_call_super
from ..factorys import add_styled, make_styled
from ..styles import current_styles


class StyledJsonLexer(QsciLexerJSON):

    def defaultPaper(self, style: int) -> QColor:
        return QColor(current_styles.editor_json['paper']['background'])

    def defaultColor(self, style: int) -> QColor:
        color = current_styles.get_editor_color(current_styles.editor_json.get('color'), style)
        if color:
            return QColor(color)
        return QColor('')

    def defaultFont(self, p_int):
        font: QFont = super().defaultFont(p_int)
        font_family = current_styles.editor_json.get('font', {}).get('default', None)
        if font_family is not None:
            font.setFamily(font_family)
            font.setPointSizeF(10)
            font.setBold(False)
        return font


@register(file_types=['json', 'ipynb'])
class JsonCodeWidget(TabCodeWidget):
    file_type = 'json'
    file_loaded = pyqtSignal()

    @must_call_super(TabCodeWidget)
    def render_custom_style(self):
        handler = current_styles.handler
        try:
            StylesHelper.set_v_history_style_dynamic(self.expression_line, color=handler, background='transparent',
                                                     width=10)
            StylesHelper.set_h_history_style_dynamic(self.expression_line, color=handler, background='transparent',
                                                     height=10)
            self.expression_line.setStyleSheet(
                'QTextEdit{background:%s;color:%s;padding:5px;font-family:微软雅黑;border:1px solid %s}' % (
                    current_styles.background_lighter, current_styles.foreground, current_styles.border
                ))
        except:
            pass

    def after_init(self):
        def clicked():
            cap = self.main_app.get_lsp_capacities(self.lsp_serve_name())
            if cap and cap.document_symbol_provider:
                if len(self.code.current_symbols) == 0:
                    self.code.onTextDocumentDocumentSymbol(self.file_path())
                else:
                    self.lsp_render.render_symbols(self.code.current_symbols, 0, 0, self.code.currentPosition())

        self.code.click_signal.connect(clicked)
        self.define_indicators()
        self.code._has_alt_control = False
        self.code.support_language_parse = True
        self.file_loaded.connect(lambda: self.code.onTextDocumentDidOpen(self.file_path(),
                                                                         'python', 0, self.code.text()
                                                                         ))

    def define_indicators(self):
        editor = self.code

        editor: QsciScintillaCompat

        editor.indicatorDefine(editor.StraightBoxIndicator, self.code.indic_brace)
        editor.setIndicatorDrawUnder(True, self.code.indic_brace)
        editor.setIndicatorForegroundColor(QColor('red'), self.code.indic_brace)
        editor.setMatchedBraceIndicator(self.code.indic_brace)
        editor.setIndicatorAlpha(self.code.indic_brace, 200)
        editor.setIndicatorOutAlpha(self.code.indic_brace, 0)

        editor.indicatorDefine(editor.StraightBoxIndicator, self.code.indic_ref)
        editor.setIndicatorDrawUnder(True, self.code.indic_ref)
        editor.setIndicatorForegroundColor(QColor(current_styles.editor_python['statics'].get('indic_ref')
                                                  ), self.code.indic_ref)

        editor.indicatorDefine(editor.StraightBoxIndicator, self.code.indic_ref_class)
        editor.setIndicatorDrawUnder(True, self.code.indic_ref_class)
        editor.setIndicatorForegroundColor(QColor(current_styles.editor_python['statics'].get('indic_ref_class')
                                                  ), self.code.indic_ref_class)

        editor.indicatorDefine(editor.StraightBoxIndicator, self.code.indic_ref_define)
        editor.setIndicatorDrawUnder(True, self.code.indic_ref_define)
        editor.setIndicatorForegroundColor(QColor(current_styles.editor_python['statics'].get('indic_ref_define')
                                                  ), self.code.indic_ref_define)

        editor.indicatorDefine(editor.SquigglePixmapIndicator, self.code.indic_diagnostics)
        editor.setIndicatorDrawUnder(True, self.code.indic_diagnostics)
        editor.setIndicatorForegroundColor(QColor('red'), self.code.indic_diagnostics)

    @cached_property
    def parser(self):
        from jmespath import lexer
        values = lexer.Lexer().tokenize(self.code.text())
        return list(values)

    def set_lexer(self):
        return StyledJsonLexer(self)

    def set_splitter_factor(self, index) -> int:
        if index == 0:
            return 300
        elif index == 1:
            return 300

    def set_splitter_widgets(self) -> List[QWidget]:
        return [self._create_jmes_path_panel()]

    def _jmes_path_search(self):
        def _search():
            json_data = json.loads(self.code.text())
            ret = jmespath.search(self.expression_line.toPlainText().strip(), json_data)
            return ret

        def call_back(ret):
            self.jmespath_json.clear()
            self.jmespath_json.setText(json.dumps(ret, ensure_ascii=False, indent=4))

        def err_back(error):
            self.jmespath_json.clear()
            self.jmespath_json.setText(str(error))

        if self.expression_line.toPlainText().strip():
            worker = self.code.get_or_create_worker('jmes-search')
            worker.add_task(_search, call_back=call_back, err_back=err_back)
        else:
            self.jmespath_json.clear()

    def _create_jmes_path_panel(self):
        def _sub_func(match: re.Match):
            g3 = match.group(3)
            if g3 == '':
                return f'[{match.group(2)}]'
            else:
                return f'[{match.group(2)}].'

        def _convert():
            text = self.expression_line.toPlainText().strip()
            if text.startswith('/'):
                text = text.replace('/', '', 1)
            text = text.replace('/', '.')
            res = re.sub(r'(\.)(\d+)(\.?)', _sub_func, text)

            self.expression_line.setText(res)

        def _hide():
            self.splitter.setSizes([1000, 0])

        widget = QWidget()
        v = QVBoxLayout(widget)
        v.setContentsMargins(0, 0, 0, 0)

        top_w = QWidget()
        top_lay = QHBoxLayout(top_w)
        top_lay.setContentsMargins(0, 0, 2, 0)

        self.clear_btn = QPushButton('清除', clicked=lambda: self.expression_line.clear())
        self.convert_btn = QPushButton('转换JSON指针', clicked=_convert)
        self.hide_btn = QPushButton(QIcon(':/icon/减号.svg'), '', clicked=_hide)
        self.hide_btn.setToolTip('隐藏')
        # self.hide_btn.setIconSize(QSize(10, 10))

        add_styled(self.clear_btn, 'bottom-button')
        add_styled(self.convert_btn, 'bottom-button')
        add_styled(self.hide_btn, 'border-button')
        top_lay.addWidget(self.clear_btn)
        top_lay.addWidget(self.convert_btn)
        top_lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
        top_lay.addWidget(self.hide_btn)
        v.addWidget(top_w)

        lay = QSplitter(Qt.Vertical)
        v.addWidget(lay)

        lay.setContentsMargins(0, 0, 0, 0)
        line = QTextEdit()
        line.textChanged.connect(self._jmes_path_search)
        line.setPlaceholderText('JmesPath 表达式')
        lay.addWidget(line)
        output = self.make_qsci_widget(self.render_custom_style, simple_search=True, multi_line=False)
        lay.addWidget(output)
        lay.setSizes([300, 600])

        self.expression_line = line
        self.jmespath_json = output

        return widget

    def capacities(self) -> int:
        editor = self.code
        return editor.ref_flag | editor.rename_flag | editor.infer_flag | editor.completion_flag  # | editor.hover_flag

    def when_remove(self):
        if getattr(self.code, '_debounce_timer', None):
            self.code._debounce_timer.stop()
        self.code.onTextDocumentDidClose(self.file_path())

    def set_bottom_code_widgets(self) -> List[QWidget]:

        return [self.navigator_bar]

    class NavigatorButton(QWidget):
        def __init__(self, txt: str, draw_arrow=True):
            super().__init__()
            self.bk = QColor(current_styles.editor_json['paper']['background'])
            self.fk = QColor(current_styles.button_hover)
            self.hover = False
            self.draw_arrow = draw_arrow
            self.txt = txt
            self.fm = QFontMetricsF(QFont('微软雅黑', 10))
            self.fm_h = self.fm.height() * 1.4
            self.fm_w = self.fm.width(self.txt) + 20
            self.setFixedHeight(self.fm_h)
            self.setFixedWidth(self.fm_w)
            self.font = QFont('微软雅黑', 10)

        def enterEvent(self, a0: QEvent) -> None:
            super().enterEvent(a0)
            self.hover = True
            self.update()

        def leaveEvent(self, a0: QEvent) -> None:
            super().leaveEvent(a0)
            self.hover = False
            self.update()

        def paintEvent(self, a0: 'QPaintEvent') -> None:
            super().paintEvent(a0)
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing, True)
            w = self.width()
            h = self.height()
            if self.hover:
                painter.fillRect(self.rect(), self.fk)
            else:
                painter.fillRect(self.rect(), self.bk)

            painter.setPen(QColor(current_styles.foreground))
            painter.setFont(self.font)
            x = (self.fm_w - w) / 2
            y = (self.fm_h - h) / 2
            painter.drawText(self.rect().adjusted(x, y, -x, -y), Qt.AlignHCenter | Qt.AlignVCenter, self.txt, )
            # draw arrow
            if self.draw_arrow:
                icon = ':/icon/箭头_列表向右.svg'
                x1 = w - 8
                y1 = h / 6

                x2 = 0
                y2 = h / 6
                painter.drawPixmap(self.rect().adjusted(x1, y1, -x2, -y2),
                                   QPixmap(icon).scaled(QSize(8, h * 2 / 3), transformMode=Qt.SmoothTransformation))

            painter.end()

    @cached_property
    def navigator_bar(self):
        f = QListWidget()
        f.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        f.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        f.setLayoutDirection(Qt.LeftToRight)
        f.setFlow(QListWidget.LeftToRight)
        f.setSpacing(0)
        f.setStyleSheet('QListWidget{background: %s;color: %s;font-family:微软雅黑;border:none;}' % (
            current_styles.editor_json['paper']['background'], current_styles.foreground))
        fm = QFontMetricsF(QFont('微软雅黑', 10))
        f.setFixedHeight(fm.height() * 1.4)
        return f

    def set_navigator_items(self, items: List[str]):
        self.navigator_bar.clear()
        # self.navigator_bar.addItems(items)
        length = len(items)
        for index, txt in enumerate(items):
            item = QListWidgetItem()
            item.setText(txt)
            item.setForeground(Qt.transparent)
            widget = self.NavigatorButton(txt, not (index == length - 1))
            item.setSizeHint(widget.size())
            self.navigator_bar.addItem(item)
            self.navigator_bar.setItemWidget(item, widget)
        self.navigator_bar.setCurrentRow(len(items) - 1)
        self.navigator_bar.update()

    language_client_class = StdIoLanguageClient

    @classmethod
    def lsp_init_kw(cls) -> dict:
        if cls.language_client_class is StdIoLanguageClient:
            from json_lsp.main import NODE, PATH_TO_BIN_JS
            commands = [
                r'vscode-json-languageserver.cmd', '--stdio'
            ]
            cmd2 = [NODE, PATH_TO_BIN_JS, '--stdio', ]
            p = subprocess.Popen(
                commands,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            return dict(reader=p.stdout, writer=p.stdin)

        return dict(host='127.0.0.1', port=9910)

    @classmethod
    def lsp_serve_name(cls) -> str:
        return 'vscode-json-language-server'

    @classmethod
    def clientCapacities(cls) -> ClientCapabilities:
        with LspContext() as c:
            t = c.type
            r = t.ClientCapabilities(
                text_document=t.TextDocumentClientCapabilities(
                    synchronization=t.TextDocumentSyncClientCapabilities(
                        will_save=True,
                        did_save=True
                    ),
                    references=t.ReferenceClientCapabilities(dynamic_registration=True),
                    color_provider=t.DocumentColorClientCapabilities(dynamic_registration=True),
                    publish_diagnostics=t.PublishDiagnosticsClientCapabilities(),
                    document_symbol=t.DocumentSymbolClientCapabilities(
                        hierarchical_document_symbol_support=True
                    )
                ))
            return r

    def custom_menu_support(self):
        return True

    def custom_menu_policy(self, pos: QPoint):
        if pos.x() > self.code.get_invalid_margins_width():
            menu: QMenu = make_styled(QMenu, 'menu')
            ac1 = menu.addAction('格式化')
            ac2 = menu.addAction('复制JSON指针')
            act = menu.exec_(QCursor.pos())
            if act == ac1:
                print(
                    'canformat: ',
                    self.serverCapacities().document_formatting_provider,
                    self.main_app.get_lsp_capacities(self.lsp_serve_name()).document_formatting_provider)
            elif act == ac2:
                pointer_str = []
                for i in range(self.navigator_bar.count()):
                    txt = self.navigator_bar.item(i).text()
                    pointer_str.append(txt)
                QApplication.clipboard().setText('/'.join(pointer_str))


def install_lsp_service():
    serve_name = JsonCodeWidget.lsp_serve_name()

    def _factory(main_app: 'appHint', root_uri: str):
        try:
            code = JsonCodeWidget._make_code_class()
            # print('install code: ', code, 'get obj: ', JsonCodeWidget._object())
            if code.register_to_app(main_app):
                lsp_name = JsonCodeWidget.lsp_serve_name()
                main_app.get_client(lsp_name)
                code.onInitialize(code.clientCapacities(), code.client_info(), root_uri=root_uri)
        except:
            import traceback
            traceback.print_exc()

    return serve_name, _factory
