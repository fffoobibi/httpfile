import re
from pathlib import Path
from typing import Any

from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtCore import Qt, pyqtSlot, QFile, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QCursor, QFont, QColor
from PyQt5.QtWidgets import QPushButton, QProgressBar, QSpacerItem, QSizePolicy, QApplication, QMenu

from . import register, TabCodeWidget
from .utils import make_h_panel
from ..factorys import add_styled, make_styled
from ..styles import current_styles


class StyledLexerCommon(QsciLexerCustom):

    def __init__(self, parent):
        super(StyledLexerCommon, self).__init__(parent)
        self.setColor(QColor(current_styles.foreground), 0)
        self.setFont(QFont(current_styles.editor_common['font']['default'], 9), 0)
        self.setPaper(QColor(current_styles.editor_common['paper']['background']), 0)

    def styleText(self, start, end):
        self.startStyling(start)
        self.setStyling(end - start + 1, 0)

    def language(self):
        return 'common'

    def description(self, p_int):
        if p_int == 0:
            return 'style_0'
        return ''

    def defaultColor(self, p_int):
        return QColor(current_styles.foreground)

    def defaultPaper(self, p_int):
        color = QColor((current_styles.editor_common['paper'].get('background')))
        return color

    # def defaultFont(self, p_int):
    #     f = super(StyledLexerCommon, self).defaultFont(p_int)
    #     if p_int == 0:
    #         font = QFont(current_styles.editor_common['font'].get('default'))
    #         font.setPointSize(f.pointSize())
    #         f = font
    #     return f


@register(file_types=['', 'log', 'ini', 'conf', 'cfg', 'txt'])
class TextCodeWidget(TabCodeWidget):
    file_type = 'common'
    file_loaded = pyqtSignal()

    def set_lexer(self) -> Any:
        return StyledLexerCommon(self)

    def create_dynamic_actions(self):
        if self.real_file_type in ['log']:
            lay, frame = make_h_panel()
            btn = QPushButton()
            btn.setIcon(QIcon(':/icon/log.svg'))
            btn.setText('日志拆分')
            btn.setIconSize(QSize(15, 15))
            lay.addWidget(btn)

            progress = QProgressBar()
            progress.setFixedHeight(8)
            progress.setFormat('')
            progress.setAlignment(Qt.AlignCenter)
            progress.hide()
            progress.setFixedWidth(100)
            progress.setRange(0, 100)

            btn.clicked.connect(lambda checked=True: self._split_files(progress))
            lay.addWidget(progress)
            # lay.addWidget(QPushButton('IO', clicked=self._io_demo))
            lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
            add_styled(btn, 'toolbar-button')
            return frame
        elif self.real_file_type in ['txt']:
            key1 = self.code.config_name('txtMultiline', self.__class__)
            key2 = self.code.config_name('txtShowline', self.__class__)
            k1v = self.code.settings.value(key1)
            k2v = self.code.settings.value(key2)

            def enable_multi(checked):
                print('checed ', checked)
                self.code.settings.setValue(key1, checked)
                self.enable_multi(checked)

            def show_line(checked):
                self.code.settings.setValue(key2, checked)
                self.disabled_line(checked)

            btn = QPushButton()
            btn.setIcon(QIcon(':/icon/扳手.svg'))
            menu = make_styled(QMenu, 'menu')

            a1 = menu.addAction('换行')
            a1.setCheckable(True)
            a1.setChecked(k1v)
            a1.triggered.connect(enable_multi)

            a2 = menu.addAction('行号')
            a2.setCheckable(True)
            a2.setChecked(k2v)

            a2.triggered.connect(show_line)
            btn.setMenu(menu)
            add_styled(btn, 'toolbar-button')
            return btn

        # return []

    def when_app_exit(self, main_app):
        pass

    def when_file_loaded(self):
        if self.real_file_type in ['txt']:
            key1 = self.code.config_name('txtMultiline', self.__class__)
            key2 = self.code.config_name('txtShowline', self.__class__)
            k1v = self.code.settings.value(key1)
            k2v = self.code.settings.value(key2)
            self.enable_multi(k1v)
            self.disabled_line(k2v)

    def after_init(self):
        self.file_loaded.connect(self.when_file_loaded)

    def custom_menu_support(self):
        return True

    def custom_menu_policy(self, pos):
        menu = QMenu()
        ac1 = menu.addAction('锁定选中行')
        act = menu.exec_(QCursor.pos())
        if act == ac1:
            if self.code.hasSelection():
                x1, y1, x2, y2 = self.code.getSelection()
                print(x1, y1, x2, y2)

    def when_insert(self, position: int, text: bytes, length: int, linesAdded: int, line: int):
        if self._file_loaded:
            pass
            # file = QFile(self.file_path())
            # ptr = file.map(0, file.size() + length)
            # import mmap
            # fp = open(self.file_path(), 'a+b')
            # fsize = os.stat(self.file_path()).st_size + length
            # mm = mmap.mmap(fp.fileno(), fsize)
            # print('posi ', position, text, length, fsize)
            # mm[position:position + length] = text
            # mm.close()
            # fp.close()

    @pyqtSlot()
    def _io_demo(self):
        f = QFile(r'C:\Users\fqk12\Desktop\httpfile\configs.py')
        f.open(QFile.ReadOnly)
        self.code.read(f)

        # maped = f.map(0, f.size())
        # print('mmmm ', maped.asstring())

    def _split_files(self, p: QProgressBar):
        p.show()
        file = open(self.file_path(), 'r', encoding='utf-8')
        file_path = Path(self.file_path()).parent
        cf = Path(self.file_path()).name.split('.')[0]
        file_names = {}
        '2022-12-04 16:36:44,525 mainwidget.py [line:197] INFO: index change: 0'
        for line in file:
            QApplication.processEvents()
            ret = re.findall(r'(\d{4}-\d{2}-\d{2})(\s+?\d{2}.\d{2}.\d{2})', line)
            if ret:
                file_name = f'{cf}_' + ret[0][0].replace('-', '_') + '.log'
                if file_name not in file_names:
                    f = open(file_path.joinpath(file_name).__str__(), 'a', encoding='utf-8')
                    file_names[file_name] = f
                f = file_names[file_name]
                f.write(line)
        for k, v in file_names.items():
            v.flush()
            v.close()
