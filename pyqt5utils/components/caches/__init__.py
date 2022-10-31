import asyncio
import aiohttp
import hashlib
import logging
from pathlib import Path
from typing import List, Type

from PyQt5.QtCore import QObject, pyqtSignal, QSize, Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel

from ..widgets.images import Images
from pyqt5utils.decorators import singleton


@singleton
class ImageCacheManager(object):

    def squeeze_cache(self, worker: 'BackgroundWorker') -> None:
        def _():
            current_cache: Path = ImageLabel.provider.instance().cache_dir
            max_cache_size = ImageLabel.provider.dft_total_size
            cache_list = sorted(current_cache.iterdir(), key=lambda _f: _f.stat().st_ctime, reverse=True)
            size = 0
            delete_list = []
            for index, d in enumerate(cache_list):
                size += d.stat().st_size
                if size >= max_cache_size:
                    delete_list = cache_list[index:]
                    break
            for f in delete_list:
                try:
                    f.unlink()
                except:
                    pass

        worker.add_task(_)

    @property
    def cache_dir(self):
        return ImageLabel.provider.dft_cache_dir

    @property
    def cache_single_min_size(self):
        return ImageLabel.provider.dft_min_size

    def set_cache_dir(self, path: str) -> None:
        ImageLabel.provider.dft_cache_dir = path

    def set_cache_single_min_size(self, value) -> None:
        ImageLabel.provider.dft_min_size = value

    def set_cache_total_size(self, value) -> None:
        ImageLabel.provider.dft_total_size = value


class ImageDownloader(object):

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
            # await asyncio.sleep(5)
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
    dft_total_size = 1024 * 1024 * 50  # 50mb

    @classmethod
    def instance(cls):
        return cls()

    def __init__(self) -> None:
        super().__init__()
        self.down_loader = ImageDownloader
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)

    @property
    def min_size(self):
        return self.dft_min_size

    @property
    def cache_dir(self) -> Path:
        path = Path(self.dft_cache_dir)
        if not path.exists():
            path.mkdir(parents=True)
        return Path(self.dft_cache_dir)

    def set_downloader(self, downloader):
        self.down_loader = downloader

    def get_images(self, urls, logger, target: QWidget, worker: 'BackgroundWorker', ok_signal: pyqtSignal,
                   fail_signal: pyqtSignal,
                   save_field: str = '_out_puts'):
        self.down_loader.fetch_images(
            urls, self.cache_dir, self.min_size, logger, ok_signal, fail_signal, target, save_field, worker)


class ImageLabel(QLabel):
    provider: Type[ImageProvider] = ImageProvider
    logger = logging.getLogger('image-downloader')
    fail_picture: str = None
    loading_gif: str = None

    _ok_signal = pyqtSignal()
    _fail_signal = pyqtSignal(str)
    _show_signal = pyqtSignal()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._image_provider = self.provider.instance()
        self._cache_dir: Path = None
        self._image_urls: List[str] = []
        self._out_puts: List[bytes] = []
        self._is_loading: bool = None
        self._loading_size: QSize = QSize(70, 70)
        self._ok_signal.connect(self._ok_slot)
        self._fail_signal.connect(self._fail_slot)
        self._show_signal.connect(self._show_slot)
        self.setAlignment(Qt.AlignCenter)

    def set_provider(self, provider):
        self._image_provider = provider

    def set_image_urls(self, urls: List[str], worker: 'BackgroundWorker'):
        self._image_urls = urls
        self._out_puts = [None] * len(urls)
        # g1 = r"C:\Users\admin\Desktop\新建文件夹\sources\gif\gif\2.gif"
        self._start_gif(self.loading_gif)  # g1
        self._is_loading = True
        self._image_provider.get_images(
            urls, self.logger, self, worker, self._ok_signal, self._fail_signal)

    def _start_gif(self, gif: str):
        self._movie = QMovie(gif)
        self._movie.setSpeed(150)
        self.setScaledContents(False)
        self.setMovie(self._movie)
        self.setMinimumSize(self._loading_size)
        self.setMaximumSize(self._loading_size)
        self._movie.start()

    def _show_slot(self):
        if not self._is_loading and all(self._out_puts):
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
                QPixmap(self.fail_picture or r'C:\Users\fqk12\Desktop\pyqt5_pay_tool\sources\失败.svg'))
        self._is_loading = False

    def mousePressEvent(self, ev: 'QMouseEvent') -> None:
        super().mousePressEvent(ev)
        if not self._is_loading and ev.button() == Qt.LeftButton:
            self._show_signal.emit()
