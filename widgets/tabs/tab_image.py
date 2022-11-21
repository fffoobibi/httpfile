from pathlib import Path
from typing import Any, List

from PyQt5.Qsci import QsciLexerXML
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QPainter, QCursor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from . import register, TabCodeWidget
from ..factorys import make_styled
from ..utils import hum_convert


@register(file_types=['png', 'jpg', 'jpeg'])
class ImageCodeWidget(TabCodeWidget):
    file_loaded = pyqtSignal()
    file_type = 'image'

    support_code = False

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

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)

        fr = QWidget()
        fr_l = QHBoxLayout(fr)
        fr_l.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
        fr_l.addWidget(label)
        fr_l.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
        lay.addWidget(fr, 1)
        self.label = label
        return [widget]

    def after_init(self):
        self.file_loaded.connect(self.when_file_loaded)
        self.file_size = None

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
        size = Path(self.file_path()).stat().st_size
        pixmap = QPixmap(f'{self.file_path()}')
        pix_size = pixmap.size()
        pw, ph = pix_size.width(), pix_size.height()
        max_size = self.size()
        mw, mh = max_size.width() - 20 * 2, max_size.height() - 20 * 2
        self.file_size = pix_size
        if pw >= mw or ph >= mh:
            # f * pw = mw
            f = mw / pw
            scaled_h = ph * f
            pixmap = pixmap.scaled(mw, scaled_h, transformMode=Qt.SmoothTransformation)
        self.label.setPixmap(pixmap)
        w, h = pixmap.width(), pixmap.height()
        msg = f'{w} x {h} {hum_convert(size)}'
        self.info_label.setText(msg)

    def resizeEvent(self, a0: 'QResizeEvent') -> None:
        super().resizeEvent(a0)
        if self.file_size is not None:
            pix_size = self.file_size
            max_size = self.size()
            pw, ph = pix_size.width(), pix_size.height()
            mw, mh = max_size.width() - 20 * 2, max_size.height() - 20 * 2
            if pw >= mw or ph >= mh:
                f = mw / pw
                scaled_h = ph * f
                pixmap = QPixmap(self.file_path()).scaled(mw, scaled_h, transformMode=Qt.SmoothTransformation)
                self.label.setPixmap(pixmap)
