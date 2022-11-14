from typing import Any, List

from PyQt5.Qsci import QsciLexerXML
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QPainter, QCursor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from . import register, TabCodeWidget
from ..factorys import make_styled


@register(file_types=['svg'])
class SVGCodeWidget(TabCodeWidget):
    file_loaded = pyqtSignal()

    def set_lexer(self) -> Any:
        return QsciLexerXML(self)

    def set_splitter_widgets(self) -> List[QWidget]:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(0, 0, 0, 0)

        frame = QWidget()
        frame_lay = QHBoxLayout(frame)
        frame_lay.setContentsMargins(0, 0, 10, 0)
        frame_lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
        info_label = QLabel()
        frame_lay.addWidget(info_label)
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

    def when_file_loaded(self):
        # self.label.load(self.code.text().encode())
        pixmap = QPixmap(f'{self.file_path()}')
        self.label.setPixmap(pixmap)
        w, h = pixmap.width(), pixmap.height()
        self.info_label.setText(f'{w}x{h}')

    def render_svg(self):
        if self._file_loaded:
            # self.label.load(self.code.text().encode())
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
