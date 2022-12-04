from pathlib import Path
from typing import Any, List

from PyQt5.Qsci import QsciLexerMarkdown
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtWidgets import QTextBrowser, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QMenu, QAction, QPushButton

from pyqt5utils.components.styles import StylesHelper
from . import register, TabCodeWidget
from .helpers import widget_debounce
from ..factorys import make_styled
from ..styles import current_styles


class StyledMarkDownLexer(QsciLexerMarkdown):

    def defaultPaper(self, style: int) -> QColor:
        try:
            return QColor(current_styles.editor_markdown['paper']['background'])
        except:
            return super().defaultPaper(style)

    def defaultColor(self, style: int) -> QColor:
        color = current_styles.get_editor_color(current_styles.editor_markdown.get('color'), style)
        if color:
            return QColor(color)
        return QColor('')


@register(file_types=['md'])
class MarkDownCodeWidget(TabCodeWidget):
    file_loaded = pyqtSignal()
    file_type = 'markdown'

    def render_custom_style(self):
        super(MarkDownCodeWidget, self).render_custom_style()
        fore = current_styles.foreground
        back = current_styles.editor_markdown.get('paper', {}).get('background')
        border = current_styles.border
        StylesHelper.set_h_history_style_dynamic(self.mark_down, color=current_styles.handler, background='transparent', height=8)
        StylesHelper.set_v_history_style_dynamic(self.mark_down, color=current_styles.handler, background='transparent', width=8)
        self.mark_down.setStyleSheet('QTextBrowser{background:%s;color:%s;font-family:微软雅黑;border:1px solid %s}' % (back, fore, border))

    def set_lexer(self) -> Any:
        return StyledMarkDownLexer(self)

    def set_splitter_factor(self, index) -> int:
        if index == 0:
            return 500
        if index == 1:
            return 200

    def set_splitter_widgets(self) -> List[QWidget]:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.mark_down = mark_down = QTextBrowser()
        self.mark_down.setAlignment(Qt.AlignCenter)
        lay.addWidget(mark_down, 1)

        return [widget]

    def after_init(self):
        self.file_loaded.connect(self.when_file_loaded)
        self.code.setContextMenuPolicy(Qt.CustomContextMenu)
        self.code.customContextMenuRequested.connect(self.define_code_menu)
        widget_debounce(self.code, self.render_markdown, self.code.textChanged, 600)

    def define_code_menu(self):
        menu: QMenu = make_styled(QMenu, 'menu')
        ac1 = menu.addAction('格式化')
        action_list = current_styles.theme_list()
        if action_list:
            actions = []
            for action in action_list:
                actions.append(menu.addAction(action))

        act = menu.exec_(QCursor.pos())

        if act == ac1:
            import xml.dom.minidom as mini
            try:
                xml = mini.parseString(self.code.text())
                txt = xml.toprettyxml()
                self.code.setText(txt)
            except:
                import traceback
                traceback.print_exc()
        else:
            if act in actions:
                current_styles.change(act.text())

    def when_file_loaded(self):
        self.render_markdown()

    def render_markdown(self):
        if self._file_loaded:
            content = self.code.text()
            self.mark_down.setMarkdown(content)

    def create_dynamic_actions(self):
        return [QPushButton('大吉吧',clicked=lambda :print('11111'))]