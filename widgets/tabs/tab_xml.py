from typing import Any

from PyQt5.Qsci import QsciLexerXML
from PyQt5.QtGui import QColor

from . import register, TabCodeWidget
from ..styles import current_styles


class StyledXmlLexer(QsciLexerXML):

    def defaultPaper(self, style: int) -> QColor:
        return QColor(current_styles.editor_xml['paper']['background'])

    def defaultColor(self, style: int) -> QColor:
        color = current_styles.get_editor_color(current_styles.editor_xml.get('color'), style)
        if color:
            return QColor(color)
        return QColor('')


@register(file_types=['xml', 'ui', 'qrc'])
class XMLCodeWidget(TabCodeWidget):
    file_type = 'xml'

    def set_lexer(self) -> Any:
        return StyledXmlLexer(self)
