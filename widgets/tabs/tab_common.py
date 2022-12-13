import os
import re
from pathlib import Path
from typing import Any

from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtCore import Qt, pyqtSlot, QFile, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QCursor, QFont, QColor
from PyQt5.QtWidgets import QPushButton, QProgressBar, QSpacerItem, QSizePolicy, QApplication, QMenu, QListWidget, \
    QLabel, QListWidgetItem

from pyqt5utils.components.styles import StylesHelper
from pyqt5utils.components.widgets.dialogs import ShadowDialog
from . import register, TabCodeWidget
from .utils import make_h_panel
from ..factorys import add_styled, make_styled
from ..styles import current_styles


class StyledLexerCommon(QsciLexerCustom):

    def __init__(self, parent, font_size=9):
        super(StyledLexerCommon, self).__init__(parent)
        self.setColor(QColor(current_styles.foreground), 0)
        self.setFont(QFont(current_styles.editor_common['font']['default'], font_size), 0)
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
            font_size = self.code.config_name('textSize', self.__class__)
            k1v = self.code.settings.value(key1)
            k2v = self.code.settings.value(key2)
            fv = self.code.settings.value(font_size) or 9

            def enable_multi(checked):
                self.code.settings.setValue(key1, checked)
                self.code.enable_multi(checked)

            def show_line(checked):
                self.code.settings.setValue(key2, checked)
                self.code.disabled_line(checked)

            def create_font_():
                font_btn = make_styled(QPushButton, 'toolbar-button')
                font_sub_btn = make_styled(QPushButton, 'toolbar-button')
                chapter_btn = make_styled(QPushButton, 'toolbar-button')

                font_btn.clicked.connect(_add_font)
                font_sub_btn.clicked.connect(_sub_font)
                chapter_btn.clicked.connect(_extrace_chapters)

                font_btn.setText('放大')
                font_sub_btn.setText('减小')
                chapter_btn.setText('目录')
                return font_btn, font_sub_btn, chapter_btn  # , line

            def _exec_script():
                text = self.sender().text().strip()
                if text:
                    exec(text, {'self': self})
                    self.sender().setFocus(True)

            def _go_to_chapter(item: QListWidgetItem):
                line = item.data(Qt.UserRole)
                self.move_to(line, 0, True)
                if self.code.wrapMode() == self.code.SC_WRAP_NONE:
                    self.code.setFirstVisibleLine(line)
                else:
                    pass
                    # self.code.ensureLineVisible(line)
                    # self.code.setFirstVisibleLine(line)
                    # self.code.ensureLineVisible(line)

            def _show_chapters(ch_list):
                style_sheet = '#FrameLess{background:%s;border:1px solid %s}' % (current_styles.background_darker,
                                                                                 current_styles.border)
                sh = ShadowDialog(frame_less_style=style_sheet, shadow_color='transparent')
                listview = QListWidget()
                for index, chapter in ch_list:
                    item = QListWidgetItem()
                    item.setText(chapter)
                    item.setData(Qt.UserRole, index)
                    listview.addItem(item)
                listview.itemDoubleClicked.connect(_go_to_chapter)
                listview.setStyleSheet(
                    'QListWidget{border:none;background:%s;color:%s}' % (
                        current_styles.background_lighter, current_styles.foreground))
                StylesHelper.set_h_history_style_dynamic(listview, color=current_styles.handler,
                                                         background='transparent',
                                                         height=10)
                StylesHelper.set_v_history_style_dynamic(listview, color=current_styles.handler,
                                                         background='transparent',
                                                         width=10)
                title = QLabel()
                title.setAlignment(Qt.AlignCenter)
                title.setStyleSheet('QLabel{font-family:微软雅黑;padding:4px;color:%s}' % current_styles.foreground)
                title.setText(f'章节')

                sh.add_content(title)
                sh.add_content(listview)
                sh.pop(self.sender())

            def _extrace_chapters():
                chapter = self.peek_store_data('txtChapters')
                if len(chapter) == 0:
                    with open(self.file_path(), 'r', encoding='utf-8') as f:
                        i = -1
                        chapter_list = []
                        for line in f:
                            QApplication.processEvents()
                            i += 1
                            if re.search('第.*?章', line):
                                chapter_list.append([i, line.strip()])
                    self.store_data(chapter_list, 'txtChapters')
                chapter_list = chapter[0]
                _show_chapters(chapter_list)

            def _add_font():
                lexer = self.code.lexer()
                f = lexer.defaultFont(0)
                size = f.pointSize() + 1
                f.setPointSize(size)
                lexer.setDefaultFont(f)
                lexer.setFont(f, 0)
                self.code.settings.setValue(font_size, size)

            def _sub_font():
                lexer = self.code.lexer()
                f = lexer.defaultFont(0)
                size = f.pointSize() - 1
                f.setPointSize(size)
                lexer.setDefaultFont(f)
                lexer.setFont(f, 0)
                self.code.settings.setValue(font_size, size)

            lay, pannel = make_h_panel()
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
            lay.addWidget(btn)

            b1, b2, b3 = create_font_()
            lay.addWidget(b1)
            lay.addWidget(b2)
            lay.addWidget(b3)
            # lay.addWidget(line)

            lexer = self.code.lexer()
            dft = lexer.defaultFont(0)
            dft.setPointSize(fv)
            lexer.setDefaultFont(dft)
            lexer.setFont(dft, 0)

            return pannel

        # return []

    def when_app_exit(self, main_app):
        pass

    def when_remove(self):
        if self.real_file_type in ['txt']:
            try:
                cfs = self.code.config_name('textPosition', self.__class__)
                current = self.code.currentPosition()
                value = self.code.settings.value(cfs) or {self.file_path(): current}
                value[self.file_path()] = current
                value['percent'] = self.code.verticalScrollBar().value() / self.code.verticalScrollBar().maximum()
                self.code.settings.setValue(cfs, value)
            except:
                pass

    def when_load_file(self):
        if self.real_file_type in ['txt']:
            key1 = self.code.config_name('txtMultiline', self.__class__)
            key2 = self.code.config_name('txtShowline', self.__class__)
            k1v = self.code.settings.value(key1)
            k2v = self.code.settings.value(key2)
            self.code.enable_multi(k1v)
            self.code.disabled_line(k2v)

    def when_file_loaded(self):
        if self.real_file_type in ['txt']:
            cfs = self.code.config_name('textPosition', self.__class__)
            current = self.code.currentPosition()
            value = self.code.settings.value(cfs) or {self.file_path(): current,
                                                      'percent': 0}
            current = value.get(self.file_path(), 0)
            line, index = self.code.lineIndexFromPosition(current)
            self.move_to(line, index, True)
            self.code.ensureCursorVisible()

    def after_init(self):
        self.file_loaded.connect(self.when_file_loaded)
        # self.code.setEolVisibility(True)

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
            import mmap
            fsize = os.stat(self.file_path()).st_size + length
            fp = open(self.file_path(), 'a+b')
            mm = mmap.mmap(fp.fileno(), fsize)
            if position == self.code.length() - 1:
                # append
                mm[position:position + length] = text
            else:
                # insert
                mm.move(position + length, position, fsize - position - length)
                mm[position:position + length] = text
            mm.close()
            fp.close()

    def when_delete(self, position: int, text: bytes, length: int, linesAdded: int, line: int):
        if self._file_loaded:
            if text is not None:
                print('position ', position, length, text, linesAdded, line)
                fp = open(self.file_path(), "a+b")
                import mmap
                mm = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_WRITE)
                f_size = mm.size()
                mm[position:] = mm[position + length:] + b' ' * length
                mm.flush()
                mm.close()
                fp.seek(f_size - length, 0)
                fp.truncate()
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
