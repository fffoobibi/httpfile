import json
import pprint
import re
import subprocess
from typing import List

import jmespath
from PyQt5.Qsci import QsciLexerJSON
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QFontMetricsF, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QTextEdit, QHBoxLayout, QPushButton, \
    QSpacerItem, QSizePolicy, QLabel, QFrame, QListWidget
from attrs import asdict
from cached_property import cached_property
from lsprotocol.types import ClientCapabilities

from lsp.interface import StdIoLanguageClient
from lsp.utils import LspContext
from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.qsci.scintillacompat import QsciScintillaCompat
from . import register, TabCodeWidget
from ..factorys import add_styled
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

    def render_custom_style(self):
        self.code.setIndentationGuidesForegroundColor(
            QColor(current_styles.guides_foreground)) if current_styles.guides_background else None
        self.code.setIndentationGuidesBackgroundColor(
            QColor(current_styles.guides_background)) if current_styles.guides_background else None

        handler = current_styles.handler
        StylesHelper.set_v_history_style_dynamic(self.code, color=handler, background='transparent', width=10)
        StylesHelper.set_h_history_style_dynamic(self.code, color=handler, background='transparent', height=10)
        if current_styles.editor_json['margin'].get('background', None):
            self.code.setMarginsBackgroundColor(QColor(current_styles.editor_json['margin'].get('background')))
            self.code.setFoldMarginColors(QColor('#404040'), QColor('#404040'))
        if current_styles.editor_json['margin'].get('foreground', None):
            self.code.setMarginsForegroundColor(QColor(current_styles.editor_json['margin'].get('foreground')))
        if current_styles.editor_json['caret'].get('foreground', None):
            self.code.setCaretLineBackgroundColor(QColor(current_styles.editor_json['caret'].get('foreground')))
        if current_styles.editor_json['caret'].get('background', None):
            self.code.setCaretForegroundColor(QColor(current_styles.editor_json['caret'].get('background')))
        if current_styles.editor_json['selection'].get('background', None):
            self.code.setSelectionBackgroundColor(
                QColor(current_styles.editor_json['selection'].get('background')))
            self.code.resetSelectionForegroundColor()
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
        output = self.make_qsci_widget(self.render_custom_style, simple_search=True)
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

    @cached_property
    def navigator_bar(self):
        f = QListWidget()
        f.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        f.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        f.setLayoutDirection(Qt.LeftToRight)
        f.setFlow(QListWidget.LeftToRight)
        f.setSpacing(0)
        f.setStyleSheet('QListWidget{background: %s;color: %s;font-family:微软雅黑}' % (
            current_styles.editor_json['paper']['background'], current_styles.foreground))
        fm = QFontMetricsF(QFont('微软雅黑'))
        # fl = QHBoxLayout(f)
        # fl.setSpacing(0)
        # fl.setContentsMargins(0, 0, 0, 0)
        f.setFixedHeight(fm.height() + 4)
        return f

    def set_navigator_items(self, items: List[str]):
        self.navigator_bar.clear()
        self.navigator_bar.addItems(items)
        self.navigator_bar.setCurrentRow(len(items) - 1)
        self.navigator_bar.update()

    language_client_class = StdIoLanguageClient

    def lsp_init_kw(self) -> dict:
        if self.language_client_class is StdIoLanguageClient:
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

    def lsp_serve_name(self) -> str:
        return 'vscode-json-language-server'

    def clientCapacities(self) -> ClientCapabilities:
        with LspContext() as c:
            t = c.type
            r = t.ClientCapabilities(text_document=t.TextDocumentClientCapabilities(
                references=t.ReferenceClientCapabilities(dynamic_registration=True),
                color_provider=t.DocumentColorClientCapabilities(dynamic_registration=True),
                publish_diagnostics=t.PublishDiagnosticsClientCapabilities(),
                document_symbol=t.DocumentSymbolClientCapabilities(
                    hierarchical_document_symbol_support=True
                )
            ))
            return r
