from typing import Any

from PyQt5.Qsci import QsciLexerSQL
from PyQt5.QtGui import QColor, QFont

from pyqt5utils.components.styles import StylesHelper
from . import register, TabCodeWidget
from ..styles import current_styles


class StyledLexerSQL(QsciLexerSQL):
    def defaultFont(self, p_int):
        font: QFont = super().defaultFont(p_int)
        font_family = current_styles.editor_sql.get('font', {}).get('default', None)
        if font_family is not None:
            font.setFamily(font_family)
        return font

    def defaultPaper(self, style: int) -> QColor:
        return QColor(current_styles.editor_sql['paper']['background'])

    def defaultColor(self, style: int) -> QColor:
        color = current_styles.get_editor_color(current_styles.editor_sql.get('color'), style)
        if color:
            return QColor(color)
        return QColor('')


@register(file_types=['sql'])
class SQlCodeWidget(TabCodeWidget):
    file_type = 'sql'

    def set_lexer(self) -> Any:
        return StyledLexerSQL(self)

    def after_init(self):
        self.code.setFont(QFont('宋体'))

    def render_custom_style(self):
        self.code.setIndentationGuidesForegroundColor(QColor(current_styles.guides_foreground)) if current_styles.guides_background else None
        self.code.setIndentationGuidesBackgroundColor(QColor(current_styles.guides_background)) if current_styles.guides_background else None

        handler = current_styles.handler
        StylesHelper.set_v_history_style_dynamic(self.code, color=handler, background='transparent', width=10)
        StylesHelper.set_h_history_style_dynamic(self.code, color=handler, background='transparent', height=10)
        if current_styles.editor_sql['margin'].get('background', None):
            self.code.setMarginsBackgroundColor(QColor(current_styles.editor_sql['margin'].get('background')))
            self.code.setFoldMarginColors(QColor('#404040'), QColor('#404040'))
        if current_styles.editor_sql['margin'].get('foreground', None):
            self.code.setMarginsForegroundColor(QColor(current_styles.editor_sql['margin'].get('foreground')))
        if current_styles.editor_sql['caret'].get('foreground', None):
            self.code.setCaretLineBackgroundColor(QColor(current_styles.editor_sql['caret'].get('foreground')))
        if current_styles.editor_sql['caret'].get('background', None):
            self.code.setCaretForegroundColor(QColor(current_styles.editor_sql['caret'].get('background')))
        if current_styles.editor_sql['selection'].get('background', None):
            self.code.setSelectionBackgroundColor(
                QColor(current_styles.editor_sql['selection'].get('background')))
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
