from PyQt5.Qsci import QsciLexerHTML
from PyQt5.QtGui import QColor

from . import register, TabCodeWidget
from ..styles import current_styles


class StyledHtmlLexer(QsciLexerHTML):

    def defaultPaper(self, style: int) -> QColor:
        try:
            return QColor(current_styles.editor_html['paper']['background'])
        except:
            return super().defaultColor(style)

    def defaultColor(self, style: int) -> QColor:
        color = current_styles.get_editor_color(current_styles.editor_html.get('color'), style)
        if color:
            return QColor(color)
        return super().defaultColor(style)


@register(file_types=['html'])
class HTMLCodeWidget(TabCodeWidget):
    file_type = 'html'

    def set_lexer(self):
        return StyledHtmlLexer(self)
