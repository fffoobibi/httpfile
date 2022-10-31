# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 11:16
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : listwidgets.py
# @Software: PyCharm

from pathlib import Path
from types import MethodType
from typing import Tuple, List, Optional, Callable

from PyQt5.QtCore import pyqtSignal, Qt, QSize, QPoint, QByteArray, QBuffer
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QFont, QWheelEvent, QResizeEvent
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QWidget, QPushButton, QToolTip, QVBoxLayout, QFrame, \
    QHBoxLayout, QSpacerItem, QSizePolicy, QLabel, QFileDialog

from pyqt5utils.components.styles import Sh
from pyqt5utils.components.widgets import GifLabel, GifButton


class PageControl(object):
    """start from 1"""

    def __init__(self, current: int = 1, total: int = 0):
        self.current = current
        self.total = total

    def __str__(self):
        return f'PageControl<current:{self.current}, total: {self.total}>'

    def reset(self):
        self.current = 1
        self.total = 0

    def update_current(self):
        self.current += 1

    def update_total(self, total: int):
        self.total = total

    def update_info(self, current: int, total: int):
        self.current = current
        self.total = total

    def can_load_more(self) -> bool:
        return self.current <= self.total


class UploadListWidget(QListWidget):
    file_size_max = pyqtSignal(str)
    file_changed = pyqtSignal()
    preview_signal = pyqtSignal(QListWidgetItem)
    _signal = pyqtSignal()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._max_files = 5
        self._max_file_size = 1024 * 1024 * 2  # 默认2mb
        self.min_height = kw.pop('min_height', 90)
        self.upload_img = kw.pop('upload_img', ':/imgs/添加.svg')
        self.forbib_img = kw.pop('forbid_img', ':/imgs/禁止.svg')
        self.widget_size = kw.pop('widget_size', 80)
        self.file_changed.connect(self._signal)
        self.add_widget: QWidget = None

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSpacing(3)
        self.setStyleSheet(Sh.upload_list_page_style)
        self.horizontalScrollBar().setStyleSheet(Sh.upload_scroll_style)
        self._add_upload_state()
        self.setMinimumHeight(self.min_height)
        self.setMaximumHeight(self.min_height)

        btn_style = 'border:none;background-color: transparent'
        btn_size = QSize(18, 18)

        self.pre_btn = QPushButton(self)
        self.nex_btn = QPushButton(self)

        self.pre_btn.setFixedSize(btn_size)
        self.nex_btn.setFixedSize(btn_size)

        self.pre_btn.setIcon(QIcon(':/imgs/后退面性.svg'))
        self.nex_btn.setIcon(QIcon(':/imgs/前进面性.svg'))

        self.pre_btn.setStyleSheet(btn_style)
        self.nex_btn.setStyleSheet(btn_style)

        self.pre_btn.hide()
        self.nex_btn.hide()

        self._signal.connect(self._show_btns)

    def _show_btns(self):
        if self.add_widget is not None:
            count = self.current_file_count
            h = self.widget_size * (count + 1) + count * self.spacing()
            if h >= self.width():
                self.nex_btn.raise_()
                self.pre_btn.raise_()
                self.nex_btn.show()
                self.pre_btn.show()
            else:
                self.nex_btn.hide()
                self.pre_btn.hide()

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        w, h = self.width(), self.height()
        hh = int((h - 18) / 2)
        self.pre_btn.move(QPoint(-3, hh))
        self.nex_btn.move(QPoint(w - 15, hh))
        self._show_btns()

    def _hum_convert(self, value: int) -> Tuple[float, str]:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return round(value, 2), units[i]
            value = value / size

    def show_as_list(self):
        file_count = self.current_file_count
        if file_count:
            for index in range(self.count()):
                if index == file_count:
                    self.item(index).setHidden(True)
                else:
                    self.item(index).setHidden(False)
        else:
            try:
                self.item(0).setHidden(True)
            except:
                pass

    def show_normal(self):
        for index in range(self.count()):
            self.item(index).setHidden(False)

    def clear_files(self):
        self.clear()
        self._add_upload_state()
        self.file_changed.emit()

    def set_max_file_size(self, size: int) -> None:
        self._max_file_size = size

    def set_max_file_count(self, count: int) -> None:
        self._max_files = count

    def max_file_size(self) -> Tuple[float, str]:
        value, unit = self._hum_convert(self._max_file_size)
        return value, unit

    @property
    def current_file_count(self):
        count = self.count()
        ret = count - 1
        if ret == -1:
            return 0
        return ret

    @property
    def max_file_size_humen(self) -> str:
        value, unit = self.max_file_size()
        return f'{value}{unit}'

    def add_image_file(self, pixmap: QPixmap, fixed: bool = False) -> bool:

        def hover_enter(this, e):
            this.__class__.enterEvent(this, e)
            index = self.indexFromItem(item).row() + 1
            QToolTip.showText(QCursor.pos(), f'第{index}个')

        def left_click(this, e):
            this.__class__.mousePressEvent(this, e)
            if e.button() == Qt.LeftButton:
                self.preview_signal.emit(widget.item)

        def remove_file():
            if not fixed:
                index = item.data(Qt.UserRole)
                take_item = self.takeItem(index)
                self.removeItemWidget(take_item)
                k = -1
                for i in range(self.count()):
                    old_item = self.item(i)
                    j = old_item.data(Qt.UserRole)
                    if j is not None:
                        k += 1
                        old_item.setData(Qt.UserRole, k)

                    if j is None:
                        w = self.itemWidget(old_item)
                        if self.count() >= (self._max_files + 1):
                            w.label.setPixmap(
                                QPixmap(self.forbib_img).scaled(25, 25, transformMode=Qt.SmoothTransformation))
                            self.add_widget.text_label.setText('禁止添加')
                            w.setEnabled(False)
                        else:
                            w.label.setPixmap(
                                QPixmap(self.upload_img).scaled(30, 30, transformMode=Qt.SmoothTransformation))
                            self.add_widget.text_label.setText('请上传图片')
                            w.setEnabled(True)
                self.file_changed.emit()

        if self.can_add():
            self._remove_upload_state()
            h = self.widget_size  # 80
            image_index = self.count()
            item = QListWidgetItem()
            item.setData(Qt.UserRole, image_index)
            item.setData(Qt.UserRole + 1, fixed)
            item.setSizeHint(QSize(h, h))

            widget = QWidget()
            widget.mousePressEvent = MethodType(left_click, widget)
            widget.enterEvent = MethodType(hover_enter, widget)
            widget.item = item
            widget.setStyleSheet(
                'QWidget{border:2px dashed lightgray}QWidget:hover{border:2px dashed #426BDD}')
            widget.setFixedSize(QSize(h, h))

            lay = QVBoxLayout(widget)
            lay.setSpacing(0)
            lay.setContentsMargins(2, 2, 2, 2)

            frame = QFrame()
            frame.setStyleSheet('border:none')
            frame.setFrameShape(QFrame.NoFrame)
            frame_lay = QHBoxLayout(frame)
            frame_lay.setSpacing(0)
            frame_lay.setContentsMargins(0, 0, 0, 0)
            frame_lay.addSpacerItem(QSpacerItem(
                20, 20, hPolicy=QSizePolicy.Expanding))

            remove_btn = QPushButton()
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.setStyleSheet('''
                QPushButton{border:none;background-color: transparent;image: url(:/imgs/移除(1).svg);padding:2}
                QPushButton:hover{border:none;image: url(:/imgs/移除.svg)}''')
            remove_btn.setToolTip('移除')
            frame_lay.addWidget(remove_btn, 0)
            remove_btn.clicked.connect(remove_file)
            remove_btn.setEnabled(not fixed)
            remove_btn.setFixedSize(QSize(20, 20))
            if fixed:
                style = '''
                QPushButton{border:none;background-color: transparent;image: url(:/new/固定_fill.svg);padding:2}
                QPushButton:hover{border:none;image: url(:/new/固定_fill(1).svg)}'''
                remove_btn.setStyleSheet(style)
                remove_btn.setToolTip('')

            label = QLabel()
            label.setMaximumWidth(h - 4)
            label.setStyleSheet('border:none')
            label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            label.setAlignment(Qt.AlignCenter)
            label.setScaledContents(True)
            label.setPixmap(pixmap)

            lay.addWidget(frame, 0)
            lay.addWidget(label, 1)

            widget.label = label

            self.addItem(item)
            self.setItemWidget(item, widget)
            # widget.setToolTip(f'第{self.indexFromItem(item).row() + 1}张')

            self._add_upload_state()
            self.file_changed.emit()
            return True
        return False

    def remove_image_file(self, index: int) -> None:
        item = self.item(index)
        index = item.data(Qt.UserRole)
        if index is not None:
            take_item = self.takeItem(index)
            self.removeItemWidget(take_item)

            k = -1
            for i in range(self.count()):
                old_item = self.item(i)
                j = old_item.data(Qt.UserRole)
                if j is not None:
                    k += 1
                    old_item.setData(Qt.UserRole, k)

                if j is None:
                    w = self.itemWidget(old_item)
                    if self.count() >= (self._max_files + 1):
                        w.label.setPixmap(
                            QPixmap(self.forbib_img).scaled(25, 25, transformMode=Qt.SmoothTransformation))
                        w.text_label.setText('禁止添加')
                        w.setEnabled(False)
                    else:
                        w.label.setPixmap(
                            QPixmap(self.upload_img).scaled(30, 30, transformMode=Qt.SmoothTransformation))
                        self.add_widget.text_label.setText('请上传图片')
                        w.setEnabled(True)
            self.file_changed.emit()

    def get_upload_files(self, contain_fixed=False) -> List[bytes]:
        res = []
        for i in range(self.count()):
            item = self.item(i)
            fixed = item.data(Qt.UserRole + 1)
            data = item.data(Qt.UserRole)
            if data is not None:
                if not contain_fixed:
                    if not fixed and fixed is not None:
                        w = self.itemWidget(item)
                        pixmap = w.label.pixmap()
                        data = self._pixmap_to_bytes(pixmap)
                        res.append(data)
                else:
                    w = self.itemWidget(item)
                    pixmap = w.label.pixmap()
                    data = self._pixmap_to_bytes(pixmap)
                    res.append(data)
        return res

    def get_upload_pixmaps(self, contain_fixed=False) -> List[QPixmap]:
        res = []
        for i in range(self.count()):
            item = self.item(i)
            fixed = item.data(Qt.UserRole + 1)
            data = item.data(Qt.UserRole)
            if data is not None:
                if not contain_fixed:
                    if not fixed and fixed is not None:
                        w = self.itemWidget(item)
                        pixmap = w.label.pixmap()
                        res.append(pixmap)
                else:
                    w = self.itemWidget(item)
                    pixmap = w.label.pixmap()
                    res.append(pixmap)
        return res

    def can_add(self) -> bool:
        return self.count() < (self._max_files + 1)

    def set_max_files(self, value: int) -> None:
        self._max_files = value

    def max_file_count(self) -> int:
        return self._max_files

    def _add_upload_state(self):
        def open_file():
            file, _ = QFileDialog.getOpenFileName(self, '选择上传图片', Path.home().joinpath('desktop').__str__(),
                                                  '*.png;*.jpg;*.jpeg')
            if file:
                size = Path(file).stat().st_size
                if size >= self._max_file_size:
                    self.file_size_max.emit(self.max_file_size_humen)
                else:
                    self.add_image_file(QPixmap(file))

        def click(this, event):
            this.__class__.mousePressEvent(this, event)
            if event.button() == Qt.LeftButton:
                open_file()

        item = QListWidgetItem()
        h = self.widget_size
        item.setSizeHint(QSize(h, h))
        item.setData(Qt.UserRole, None)
        widget = QWidget()
        widget.mousePressEvent = MethodType(click, widget)
        widget.setStyleSheet(
            'QWidget{border:2px dashed lightgray; border-radius:3px}QWidget:hover{border:2px dashed #426BDD}')
        lay = QVBoxLayout(widget)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        widget.setFixedHeight(h)
        widget.setFixedWidth(h)
        widget.setCursor(Qt.PointingHandCursor)

        lay.addSpacerItem(QSpacerItem(20, 20, vPolicy=QSizePolicy.Expanding))
        label = QLabel()
        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        label.setAlignment(Qt.AlignCenter)
        label.setPixmap(QPixmap(self.upload_img).scaled(
            30, 30, transformMode=Qt.SmoothTransformation))
        label.setStyleSheet('border:none;background-color:transparent')
        lay.addWidget(label, 1)
        text_label = QLabel()
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet('font-family:微软雅黑;color: gray;border:none')
        text_label.setText('请上传图片')
        lay.addWidget(text_label, 0)
        lay.addSpacerItem(QSpacerItem(20, 20, vPolicy=QSizePolicy.Expanding))

        widget.label = label
        widget.text_label = text_label

        self.add_widget = widget

        self.addItem(item)
        self.setItemWidget(item, widget)

        if self.count() >= (self._max_files + 1):
            widget.setEnabled(False)
            text_label.setText('禁止添加')
            label.setPixmap(QPixmap(self.forbib_img).scaled(
                25, 25, transformMode=Qt.SmoothTransformation))

    def _remove_upload_state(self):
        for i in range(self.count()):
            item = self.item(i)
            data = item.data(Qt.UserRole)
            if data is None:
                self.takeItem(i)
                self.removeItemWidget(item)
                self.add_widget = None
                break

    def _pixmap_to_bytes(self, pixmap: QPixmap, format: str = 'JPG') -> Optional[bytes]:
        bytes_data = QByteArray()
        buf = QBuffer(bytes_data)
        pixmap.save(buf, 'PNG')
        data = bytes(bytes_data)
        if len(data) <= self._max_file_size:
            return data

        else:
            bytes_data = QByteArray()
            buf = QBuffer(bytes_data)
            pixmap.save(buf, format)
            data = bytes(bytes_data)

            if len(data) <= self._max_file_size:
                return data

            qua = 50

            while True:
                bytes_data = QByteArray()
                buf = QBuffer(bytes_data)
                pixmap.save(buf, format, qua)
                data = bytes(bytes_data)
                if len(data) >= self._max_file_size:
                    if qua <= 0:
                        return
                    qua -= 5
                else:
                    return data


class LoadListWidget(QListWidget):
    load_more_sig = pyqtSignal()
    loading_state = pyqtSignal()
    clear_signal = pyqtSignal()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.verticalScrollBar().actionTriggered.connect(self._load)
        self.wheel_up = None
        self.loading_index = None
        self.wait_loading = False
        self.load_flag = True
        self.loading_condition: Callable = None

        self._global_loading = GifLabel(self)
        self._global_loading.setStyleSheet(
            'border:none;background-color:transparent')
        fm = self._global_loading.fontMetrics().height()
        self._global_loading.setFixedSize(QSize(40, fm * 2))
        self._global_loading.hide()

        self._no_data = QWidget(self)
        label = QLabel()
        label.setScaledContents(True)
        label.setPixmap(QPixmap(':/imgs/缺省页_暂无数据.svg'))
        h = 60
        label.setFixedSize(QSize(h, h))
        label2 = QLabel('暂无数据')
        label2.setStyleSheet('border:none;color:gray;font-family:微软雅黑')
        hei = label2.fontMetrics().height() * 1.5
        label2.setFixedHeight(hei)
        label2.setAlignment(Qt.AlignCenter)
        lay = QVBoxLayout(self._no_data)
        lay.setSpacing(1)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.addWidget(label)
        lay.addWidget(label2)
        self._no_data.setFixedSize(QSize(h + 4, h + 5 + hei))
        self._no_data.hide()

    def clear(self):
        super().clear()
        self.clear_signal.emit()

    def add_widget(self, widget: QWidget, item_size: QSize, search_text: str = None, search_type: int = 0):
        def bind():
            widget.raw_alive = False

        if search_text is not None:
            item = self.search_item(search_text, search_type)
        else:
            item = QListWidgetItem()
        item.setSizeHint(item_size)
        self.addItem(item)
        self.setItemWidget(item, widget)
        self.clear_signal.connect(bind)

    def find_widget(self, tag: str, search_type: int = 0):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget is not None:
                if widget.tag().strip() == tag.strip():
                    return widget

    def search(self, text: str, search_type: int = 0) -> int:
        if text == '':
            for it in range(self.count()):
                item = self.item(it)
                item.setHidden(False)
            return self.count()
        else:
            i = 0
            items = self.findItems(text, Qt.MatchContains | Qt.MatchCaseSensitive)
            for it in range(self.count()):
                item = self.item(it)
                if item not in items:
                    item.setHidden(True)
                else:
                    i += 1
                    item.setHidden(False)
            return i

    def search_item(self, text: str, search_type: int = 0) -> QListWidgetItem:
        item = QListWidgetItem()
        item.setText(text)
        item.setForeground(Qt.transparent)
        return item

    def set_loding_condition(self, func: Callable):
        self.loading_condition = func

    def set_loading_enable(self, flag: bool):
        self.load_flag = flag

    def show_global_loading(self):
        self.load_flag = False
        w, h = self.width(), self.height()
        gw, gh = self._global_loading.width(), self._global_loading.height()
        sw = int((w - gw) / 2)
        sh = int((h - gh) / 2)
        self._global_loading.move(sw, sh)
        self._global_loading.show()
        self._global_loading.raise_()
        self._global_loading.setGif(':/imgs/加载2.gif')
        self.setEnabled(False)

    def hide_global_loading(self):
        self.load_flag = True
        self._global_loading.removeGif('')
        self._global_loading.hide()
        self.setEnabled(True)

    def show_no_data(self):
        self.load_flag = False
        w, h = self.width(), self.height()
        gw, gh = self._no_data.width(), self._no_data.height()
        sw = int((w - gw) / 2)
        sh = int((h - gh) / 2)
        self._no_data.move(sw, sh)
        self._no_data.show()
        self._no_data.raise_()

    def hide_no_data(self):
        self.load_flag = True
        self._no_data.hide()

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        if not self._global_loading.isHidden():
            w, h = self.width(), self.height()
            gw, gh = self._global_loading.width(), self._global_loading.height()
            sw = int((w - gw) / 2)
            sh = int((h - gh) / 2)
            self._global_loading.move(sw, sh)
        if not self._no_data.isHidden():
            w, h = self.width(), self.height()
            gw, gh = self._no_data.width(), self._no_data.height()
            sw = int((w - gw) / 2)
            sh = int((h - gh) / 2)
            self._no_data.move(sw, sh)

    def start_loading(self):
        if self.load_flag:
            condition = self.loading_condition() if self.loading_condition is not None else True
            if condition:
                self.loading_index = self.count()
                self.wait_loading = True
                self.hide_no_data()
                self.hide_global_loading()
                item = QListWidgetItem(self)
                item.setSizeHint(QSize(100, 30))
                item.setBackground(Qt.gray)
                widget = QWidget()
                widget.setFixedHeight(30)
                btn = GifButton()
                btn.setText('加载中')
                btn.setStyleSheet('border:none;font-family:微软雅黑')
                btn.setGif(':/imgs/加载2.gif')
                lay = QHBoxLayout(widget)
                lay.addWidget(btn)
                widget.setStyleSheet('background-color: transparent')
                self.setItemWidget(item, widget)
                self.load_more_sig.emit()

    def end_loading(self):
        if self.loading_index is not None:
            if self.wait_loading:
                self.hide_global_loading()
                self.hide_no_data()
                item = self.takeItem(self.loading_index)
                self.removeItemWidget(item)
                self.loading_index = None
                self.wait_loading = False

    def cant_loading(self):
        item = QListWidgetItem()
        item.setForeground(Qt.gray)
        item.setSizeHint(QSize(100, 30))
        label = QLabel()
        label.setFont(QFont('微软雅黑'))
        label.setText('一一一 到底了 一一一')
        label.setStyleSheet(
            'border:none;background-color:transparent;color:gray')
        label.setAlignment(Qt.AlignCenter)
        self.addItem(item)
        self.setItemWidget(item, label)

    def stop_loading(self):
        self.end_loading()
        self.cant_loading()
        self.load_flag = False

    def _max(self):
        return self.verticalScrollBar().maximum()

    def _load(self, v):
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            if not self.wait_loading:
                self.start_loading()

    def wheelEvent(self, e: QWheelEvent) -> None:
        super().wheelEvent(e)
        if e.angleDelta().y() < 0:
            self.wheel_up = True
        else:
            self.wheel_up = False
