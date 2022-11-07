# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 11:17
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : labels.py
# @Software: PyCharm
import asyncio
import hashlib
import logging
from pathlib import Path

import aiohttp
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QSize
from PyQt5.QtGui import QCursor, QMouseEvent, QMovie, QPixmap
from PyQt5.QtWidgets import QLabel, QMenu, QApplication, QWidget

from pyqt5utils import singleton
from pyqt5utils.components.styles import Sh


class WordWapLabel(QLabel):
    def __init__(self, *a, **kw):
        super(WordWapLabel, self).__init__(*a, **kw)
        self.setWordWrap(True)

    def setText(self, a0: str) -> None:
        super(WordWapLabel, self).setText(a0)
        self.setToolTip(a0)


class InfoLabel(QLabel):

    def _context(self, pos=None):
        menu = QMenu(self)
        menu.setStyleSheet(Sh.menu_style)
        a1 = menu.addAction('复制')
        act = menu.exec_(QCursor.pos())
        if act == a1:
            QApplication.clipboard().setText(self.raw_text)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        super(InfoLabel, self).mousePressEvent(ev)
        if ev.button() == Qt.RightButton:
            self._context()

    def _wrap(self, string, max_width=25) -> str:
        result1 = [string[i:i + max_width]
                   for i in range(0, len(string), max_width)]
        result = '\n'.join(result1)
        return result

    def __init__(self, *a, **kw):
        super(InfoLabel, self).__init__(*a, **kw)
        self._text = ''

    @property
    def raw_text(self):
        return self._text

    def setText(self, a0: str, tool_tip=True, width=40) -> None:
        super().setText(a0)
        self._text = a0
        self.setToolTip(a0, width)

    def clear(self) -> None:
        super(InfoLabel, self).clear()
        self._text = ''

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        if self._text:
            fm = self.fontMetrics()
            text = fm.elidedText(self._text, Qt.ElideRight, self.width())
            super().setText(text)

    def setToolTip(self, a0: str, width=25) -> None:
        if width is not None:
            text = self._wrap(a0, width)
        else:
            text = a0
        super().setToolTip(text)


class DotLabel(QLabel):

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        super(DotLabel, self).mousePressEvent(ev)

    def __init__(self, *a, **kw):
        super(DotLabel, self).__init__(*a, **kw)
        self._text = ''

    @property
    def raw_text(self):
        return self._text

    def setText(self, a0: str, raw_text: str = None) -> None:
        super().setText(a0)
        self._text = raw_text or a0

    def clear(self) -> None:
        super(DotLabel, self).clear()
        self._text = ''

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        if self._text:
            fm = self.fontMetrics()
            text = fm.elidedText(self._text + '  ', Qt.ElideRight, self.width())
            self.setText(text, self._text)



class Downloader(object):

    @classmethod
    def image_name(cls, url: str) -> str:
        md = hashlib.md5()
        md.update(url.encode())
        return md.hexdigest()

    @classmethod
    def fetch_images(cls, urls, cache_dir, min_size, logger, ok_signal, fail_signal, target, save_field, worker):

        caches = {f.name: True for f in cache_dir.iterdir()}

        async def _fetch_image(client, url: str, page_ind: int):
            try:
                outputs = getattr(target, save_field)
                img = cls.image_name(url)  # 优先读取缓存数据
                cache = caches.get(img)
                if cache:
                    content = cache_dir.joinpath(img).read_bytes()
                    outputs[page_ind] = content
                    return content, page_ind
                async with client.get(url) as resp:
                    resp.raise_for_status()
                    content = await resp.read()
                    try:
                        if len(content) > min_size:
                            cache_dir.joinpath(img).write_bytes(
                                content)  # 保存缓存
                    except:
                        logger.warn(f'缓存: {img} 失败', exc_info=True)
                    outputs[page_ind] = content
                    return content
            except Exception as e:
                logger.warn(f'[{page_ind}] [{url}] fetch fail: {e}')
                outputs = getattr(target, save_field)
                outputs[page_ind] = None
                return None

        async def _fetch():
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as client:
                tasks = [_fetch_image(client, u, ind)
                         for ind, u in enumerate(urls)]
                results = await asyncio.gather(*tasks)
                return results

        def call_back(ret):
            ok_signal.emit()

        def err_back(error):
            fail_signal.emit(error)

        worker.add_coro(_fetch(), call_back=call_back, err_back=err_back)


@singleton
class ImageProvider(QObject):
    dft_cache_dir = './_image_caches'

    dft_min_size = 1024 * 3

    @classmethod
    def instance(cls):
        return cls()

    def __init__(self) -> None:
        super().__init__()
        self.cache_dir: Path = Path(self.dft_cache_dir)
        self.down_loader = Downloader
        self.min_size = self.dft_min_size
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)

    def set_downloader(self, downloader):
        self.down_loader = downloader

    def get_images(self, urls, logger, target: QWidget, worker, ok_signal, fail_signal, save_field: str = '_out_puts'):
        self.down_loader.fetch_images(
            urls, self.cache_dir, self.min_size, logger, ok_signal, fail_signal, target, save_field, worker)


class ImageLabel(QLabel):
    logger = logging.getLogger('ImageLabel')
    fail_picture: str = None
    loading_gif: str = None

    _ok_signal = pyqtSignal()
    _fail_signal = pyqtSignal(str)
    _show_signal = pyqtSignal()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._image_provider = ImageProvider()
        self._cache_dir: Path = None
        self._image_urls = []
        self._out_puts = []
        self._is_loading = None
        self._loading_size = QSize(70, 70)
        self._fail_picture = None
        self._ok_signal.connect(self._ok_slot)
        self._fail_signal.connect(self._fail_slot)
        self._show_signal.connect(self._show_slot)
        self.setAlignment(Qt.AlignCenter)

    def set_image_urls(self, urls, worker):
        self._image_urls = urls
        self._out_puts = [None] * len(urls)
        g1 = r"C:\Users\admin\Desktop\新建文件夹\sources\gif\gif\2.gif"
        self._start_gif(g1)
        self._is_loading = True
        self._image_provider.get_images(
            urls, self.logger, self, worker, self._ok_signal, self._fail_signal)

    def _start_gif(self, gif):
        self._movie = QMovie(gif)
        self._movie.setSpeed(150)
        self.setScaledContents(False)
        self.setMovie(self._movie)
        self.setMinimumSize(self._loading_size)
        self.setMaximumSize(self._loading_size)
        self._movie.start()

    def _show_slot(self):
        if self._is_loading == False and all(self._out_puts):
            Images.display(self._out_puts, 'test', self, index=1)

    def _ok_slot(self):
        self._end(0)

    def _fail_slot(self, err):
        self._end(1)

    def _end(self, state=0):  # 0, success, 1 fail
        self.setMinimumSize(0, 0)
        self.setMaximumSize(10000, 10000)
        self.setScaledContents(True)
        if state == 0:
            pixmap = QPixmap()
            pixmap.loadFromData(self._out_puts[-1])
            self.setPixmap(pixmap)
        else:
            self.setPixmap(
                QPixmap(r'C:\Users\fqk12\Desktop\pyqt5_pay_tool\sources\失败.svg'))
        self._is_loading = False

    def mousePressEvent(self, ev: 'QMouseEvent') -> None:
        super().mousePressEvent(ev)
        if self._is_loading == False and ev.button() == Qt.LeftButton:
            self._show_signal.emit()
