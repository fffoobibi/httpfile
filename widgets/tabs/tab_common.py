import collections
import os
import re
from pathlib import Path
from typing import Any

from PyQt5.Qsci import QsciLexerTeX
from PyQt5.QtCore import Qt, pyqtSlot, QFile, QSize
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import QPushButton, QFrame, QProgressBar, QSpacerItem, QSizePolicy, QApplication, QMenu

from . import register, TabCodeWidget

# from PyQt5 import QsciLexerTeX
from .helpers import widget_debounce
from .utils import make_h_panel
from ..factorys import add_styled


@register(file_types=['', 'log', 'ini', 'conf', 'cfg', 'txt'])
class TextCodeWidget(TabCodeWidget):
    file_type = 'common'

    def set_lexer(self) -> Any:
        return QsciLexerTeX(self)

    def create_dynamic_actions(self):
        if self.file_path().split('.')[-1] in ['log']:
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
            lay.addWidget(QPushButton('IO', clicked=self._io_demo))
            lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
            add_styled(btn, 'toolbar-button')
            return [frame, ]

        return []

    def after_init(self):
        pass
        # self.code.customContextMenuRequested.connect(self._menu_policy)
        # widget_debounce(self.code, self._auto_save, self.code.textChanged)

    def custom_menu_support(self):
        return True

    def custom_menu_policy(self, pos):
        menu = QMenu()
        ac1 = menu.addAction('锁定选中行')
        act = menu.exec_(QCursor.pos())
        if act == ac1:
            if self.code.hasSelection():
                x1, y1, x2, y2 = self.code.getSelection()
                print(x1, y1 ,x2, y2)


    def when_insert(self, position: int, text: bytes, length: int, linesAdded: int, line: int):
        if self._file_loaded:
            # file = QFile(self.file_path())
            # ptr = file.map(0, file.size() + length)
            print('text   ', text)
            import mmap
            print(self.file_path())
            fp = open(self.file_path(), 'a+b')
            fsize = os.stat(self.file_path()).st_size + length
            mm = mmap.mmap(fp.fileno(), fsize)
            print('posi ', position, text, length, fsize)
            mm[position:position + length] = text
            mm.close()
            fp.close()

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
