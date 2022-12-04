from pathlib import Path
from typing import Any, List

from PyQt5.Qsci import QsciLexerXML
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QPainter, QCursor, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from . import register, TabCodeWidget
from ..factorys import make_styled
from ..styles import current_styles
from ..utils import hum_convert


class StyledSvgLexer(QsciLexerXML):

    def defaultPaper(self, style: int) -> QColor:
        try:
            return QColor(current_styles.editor_svg['paper']['background'])
        except:
            return super(StyledSvgLexer, self).defaultPaper(style)

    def defaultColor(self, style: int) -> QColor:
        color = current_styles.get_editor_color(current_styles.editor_svg.get('color'), style)
        if color:
            return QColor(color)
        return super().defaultColor(style)


@register(file_types=['svg'])
class SVGCodeWidget(TabCodeWidget):
    file_loaded = pyqtSignal()
    file_type = 'svg'

    def set_lexer(self) -> Any:
        return StyledSvgLexer(self)

    def set_splitter_factor(self, index) -> int:
        if index == 0:
            return 500
        if index == 1:
            return 200

    def set_splitter_widgets(self) -> List[QWidget]:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(0, 0, 0, 0)

        frame = QWidget()
        frame_lay = QHBoxLayout(frame)
        frame_lay.setContentsMargins(10, 0, 0, 0)
        info_label = QLabel()
        info_label.setStyleSheet('QLabel{color:gray}')
        frame_lay.addWidget(info_label)
        frame_lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
        self.info_label = info_label
        lay.addWidget(frame)

        self.label = label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        lay.addWidget(label, 1)

        return [widget]

    def after_init(self):
        self.file_loaded.connect(self.when_file_loaded)
        self.code.textChanged.connect(self.render_svg)
        self.code.setContextMenuPolicy(Qt.CustomContextMenu)
        self.code.customContextMenuRequested.connect(self.define_code_menu)

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
        size = Path(self.file_path()).stat().st_size
        pixmap = QPixmap(f'{self.file_path()}')
        self.label.setPixmap(pixmap)
        w, h = pixmap.width(), pixmap.height()
        msg = f'{w} x {h} {hum_convert(size)}'
        self.info_label.setText(msg)

    def render_svg(self):
        if self._file_loaded:
            content = self.code.text()
            render = QSvgRenderer()
            render.load(content.encode('utf-8'))
            pix_size = render.defaultSize()
            if pix_size.isValid():
                pixmap = QPixmap(pix_size)
                pixmap.fill(Qt.transparent)
                painter = QPainter()
                painter.begin(pixmap)
                painter.setRenderHints(QPainter.Antialiasing, True)
                render.render(painter)
                painter.end()
                self.label.setPixmap(pixmap)
