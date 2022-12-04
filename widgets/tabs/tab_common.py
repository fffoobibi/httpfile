import collections
import re
from pathlib import Path
from typing import Any

from PyQt5.Qsci import QsciLexerTeX
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QFrame, QProgressBar, QSpacerItem, QSizePolicy, QApplication

from . import register, TabCodeWidget

# from PyQt5 import QsciLexerTeX
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
            lay.addSpacerItem(QSpacerItem(20, 20, hPolicy=QSizePolicy.Expanding))
            add_styled(btn, 'toolbar-button')
            return [frame, ]

        return []

    def _split_files(self, p: QProgressBar):
        print(p)
        p.show()
        file = open(self.file_path(), 'r', encoding='utf-8')
        file_path = Path(self.file_path()).parent
        cf = Path(self.file_path()).name.split('.')[0]
        file_names = {}
        for line in file:
            '2022-12-04 16:36:44,525 mainwidget.py [line:197] INFO: index change: 0'
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
