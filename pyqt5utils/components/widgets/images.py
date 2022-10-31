# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 13:33
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : images.py
# @Software: PyCharm
import asyncio
import math
from collections import deque
from datetime import datetime
from enum import IntEnum, Enum
from pathlib import Path
from typing import Union, List, Tuple

from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QMargins, QEvent, QObject, pyqtSignal
from PyQt5.QtGui import QPen, QColor, QCursor, QPainter, QMouseEvent, QKeySequence, QIcon, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QLabel, QMenu, QWidget, QFileDialog, QApplication, QPushButton

from pyqt5utils.components.feedback import Message
from pyqt5utils.components.widgets import GifLabel

Size = Tuple[int, int]
Zoom = Tuple[float, float]
RectCoord = List[int]  # [x1,y1,x2,y2]
RectCoords = List[RectCoord]  # [[x1,y1,x2,y2], [x2,y3,x4,y4], ...]
Region = 'x1,y1,x2,y2;...'


class _Actions(Enum):
    MOVE_RECT = 0
    DRAW_RECT = 1
    NONE = 2
    ERASE = 3  # 图像编辑擦除
    NORMAL = 4  # 正常模式
    ZOOM = 5  # 缩放模式
    MOVE = 6  # 移动模式


class _Validpoints(QObject):  # [[x1,y1, x2, y2], ...]

    points_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.__data = []

    @classmethod
    def fromList(points: RectCoords):
        point = _Validpoints()
        point.appends(points)
        return point

    @classmethod
    def adjustCoords(cls, points: RectCoords) -> RectCoords:
        xycoords = []
        for coord in points:
            x1, y1, x2, y2 = coord
            w, h = abs(x2 - x1), abs(y2 - y1)
            if (x2 - x1) > 0 and (y2 - y1) > 0:
                xycoords.append([x1, y1, x2, y2])  # 右下方滑动
            elif (x2 - x1) > 0 and (y2 - y1) < 0:
                xycoords.append([x1, y1 - h, x2, y2 + h])  # 右上方滑动
            elif (x2 - x1) < 0 and (y2 - y1) > 0:
                xycoords.append([x2, y2 - h, x1, y1 + h])  # 左下方滑动
            else:
                xycoords.append([x2, y2, x1, y1])  # 左上方滑动
        return xycoords

    @property
    def data(self) -> RectCoords:
        res = []
        for v in self.__data:
            if (v[:2] != v[2:]) and (0 not in v[-2:]):
                res.append(v)
        return res

    def append(self, v: RectCoord) -> bool:
        if v[:2] != v[2:]:
            self.__data.append(v)
            return True
        return False

    def appends(self, points: RectCoords) -> None:
        for point in points:
            self.append(point)

    def appendRect(self, qrect: QRect) -> bool:
        rects = list(qrect.getCoords())
        return self.append(rects)

    def appendRects(self, qrects: List[QRect]) -> None:
        for rect in qrects:
            self.appendRect(rect)

    def appendRectslike(self, qrects_like: List[tuple]) -> None:
        for rect in qrects_like:
            self.appendRect(QRect(*rect))

    def clear(self):
        self.__data.clear()

    def __iter__(self):
        for v in self.data:
            yield v

    def __getitem__(self, item) -> RectCoord:
        return self.__data[item]

    def __repr__(self):
        return f'Validpoints<{self.data}>'


class _ImgLabel(QLabel):
    start_point: QPoint = None
    PEN = QPen(Qt.darkYellow, 2, Qt.DashLine)
    FILL_COLOR = QColor(50, 50, 50, 30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edited = True
        self.points = _Validpoints()  # 矩形区域
        self.menu = QMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setAlignment(Qt.AlignCenter)

    def setEdit(self, flag: bool):
        self.edited = flag
        self._width = self.pixmap().width()
        self._heigth = self.pixmap().height()

    def contextMenu(self, pos):
        menu = QMenu(self)
        a1 = menu.addAction('清除')
        a2 = menu.addAction('确认')
        action = menu.exec_(QCursor.pos())
        if action == a1:
            self.points.clear()
            self.points.points_signal.emit([])
            self.update()
        elif action == a2:
            points = []
            for xycoords in self.points.data:
                x1, y1, x2, y2 = xycoords
                w, h = abs(x2 - x1), abs(y2 - y1)
                if (x2 - x1) > 0 and (y2 - y1) > 0:
                    points.append([x1, y1, x2, y2])  # 右下方滑动
                elif (x2 - x1) > 0 and (y2 - y1) < 0:
                    points.append([x1, y1 - h, x2, y2 + h])  # 右上方滑动
                elif (x2 - x1) < 0 and (y2 - y1) > 0:
                    points.append([x2, y2 - h, x1, y1 + h])  # 左下方滑动
                else:
                    points.append([x2, y2, x1, y1])  # 左上方滑动
            self.points.clear()
            self.points.appends(points)
            self.points.points_signal.emit(points)

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.start_point = QMouseEvent.pos()

        if self.edited:
            if QMouseEvent.button() == Qt.LeftButton:
                self.points.append([QMouseEvent.x(), QMouseEvent.y(), 0, 0])
        else:
            super().mousePressEvent(QMouseEvent)

    def mouseMoveEvent(self, QMouseEvent):
        if self.edited:
            if (QMouseEvent.buttons()
                & Qt.LeftButton) and self.rect().contains(
                QMouseEvent.pos()):
                self.points[-1][-2:] = [QMouseEvent.x(), QMouseEvent.y()]
                self.update()
        else:
            super().mouseMoveEvent(QMouseEvent)

    def paintEvent(self, QPaintEvent):
        if self.edited:
            self.setCursor(Qt.CrossCursor)
            font = self.font()
            font.setPointSize(15)
            painter = QPainter()
            painter.begin(self)
            painter.setFont(font)
            self.drawPolicy(painter)
            painter.end()
        else:
            self.setCursor(Qt.ArrowCursor)
            super().paintEvent(QPaintEvent)

    def drawPolicy(self, painter):
        painter.drawPixmap(0, 0, self.pixmap())
        if self.points.data:
            painter.setPen(self.PEN)
            for index, point in enumerate(self.points.data, 1):
                x1, y1, x2, y2 = point
                msg = str(index)
                w, h = abs(x2 - x1), abs(y2 - y1)
                if (x2 - x1) > 0 and (y2 - y1) > 0:
                    painter.drawRect(x1, y1, w, h)  # 右下方滑动
                    painter.drawText(x1, y1 - 4, msg)
                    painter.fillRect(x1, y1, w, h, self.FILL_COLOR)
                elif (x2 - x1) > 0 and (y2 - y1) < 0:
                    painter.drawRect(x1, y1 - h, w, h)  # 右上方滑动
                    painter.drawText(x1, y2 - 4, msg)
                    painter.fillRect(x1, y1 - h, w, h, self.FILL_COLOR)

                elif (x2 - x1) < 0 and (y2 - y1) > 0:
                    painter.drawRect(x1 - w, y1, w, h)  # 左下方滑动
                    painter.drawText(x2, y1 - 4, msg)
                    painter.fillRect(x1 - w, y1, w, h, self.FILL_COLOR)

                else:
                    painter.drawRect(x2, y1 - h, w, h)  # 左上方滑动
                    painter.drawText(x2, y2 - 4, msg)
                    painter.fillRect(x2, y1 - h, w, h, self.FILL_COLOR)


class ZoomLabel(_ImgLabel):
    drag_enable = True  # 是否拖拽
    viewpoint_zoom = True  # 缩放类型: 视点缩放, 普通缩放
    resize_auto_scaled = False  # 自身尺寸变化
    action = _Actions.NONE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.NoFocus)
        self.zoomAndMoveInit()  # 缩放,移动初始化

    def zoomAndMoveInit(self):
        self.setMouseTracking(True)  # 设置光标追踪
        self.move_intention = False  # 控制拖拽移动相关的标志位
        self.zoom_intention = False  # 控制缩放相关的标志位
        self.pixmap_draw = None  # 需要绘制的图片资源
        self.pixmap_draw_rect = None  # 绘图区域,pixmap绘制在qrect中,控制qrect即可控制pixmap的拖拽,缩放等行为
        self.pixmap_raw = None
        self.pixmap_point = None
        self.pixmap_is_max = False
        self.wheel_logs = deque(maxlen=2)

    def activeAction(self):
        return self.action

    def setAction(self, action: _Actions):
        self.action = action

    def isInPixmap(self, point: QPoint):
        return self.pixmap_draw_rect.contains(point)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Control:  # 按下ctrl 进入缩放模式
            self.zoom_intention = True
            self.setCursor(Qt.PointingHandCursor)
            self.setAction(_Actions.ZOOM)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)  # 取消ctrl 取消缩放模式
        if event.key() == Qt.Key_Control:
            self.zoom_intention = False
            self.setCursor(Qt.ClosedHandCursor)
            self.action = _Actions.NORMAL

    def mousePressEvent(self, QMouseEvent: 'QMouseEvent'):
        super().mousePressEvent(QMouseEvent)
        if self.pixmap_draw:
            if QMouseEvent.button() == Qt.LeftButton:
                if self.action == _Actions.DRAW_RECT:
                    self.points.append(
                        [QMouseEvent.x(), QMouseEvent.y(), 0, 0])
                elif self.action == _Actions.ERASE:
                    self.erase_points.append(
                        [QMouseEvent.x(), QMouseEvent.y(), 0, 0])
                if self.isInPixmap(QMouseEvent.pos()):  # 初始化
                    self.move_intention = True
                    self.start_pos = QMouseEvent.pos()
                    self.pixmap_left_before = self.pixmap_draw_rect.topLeft()

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.move_intention = False

    def mouseMoveEvent(self, QMouseEvent):
        super().mouseMoveEvent(QMouseEvent)
        if self.pixmap_draw:  # 画图标志位置
            if self.drag_enable:  # 是否拖拽
                if self.isInPixmap(QMouseEvent.pos()):  # 设置移动光标样式,拖拽设置
                    if self.move_intention:
                        self.setCursor(Qt.SizeAllCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
                if self.move_intention and not self.zoom_intention:  # 拖拽图片
                    self.setAction(_Actions.MOVE)
                    self.current_pos = QMouseEvent.pos()
                    distance = self.current_pos - self.start_pos
                    self.pixmap_draw_rect.moveTo(
                        self.pixmap_left_before + distance)
                    self._moveAfterUpdateZoomParamters()
                    self.update()

    def wheelEvent(self, event: 'QWheelEvent'):
        super().wheelEvent(event)
        if self.pixmap_draw_rect.contains(event.pos()):
            self.action = _Actions.ZOOM
            self.setCursor(Qt.CrossCursor)
            self._zoomBeforeParametersCalculate(event)
            self._zoomCalculate(event)
            self._zoomAfterupdateParameters(QRect(self.pixmap_draw_rect))
            self.update()

    def setPixmap(self, pixmap):
        raise RuntimeError('use addPixmap, not setPixmap')

    # 添加显示的图片, 默认全部显示范围
    def addPixmap(self, source: str = None, point: QPoint = None, *, fixed=True,
                  margins: QMargins = QMargins(0, 0, 0, 0), action: _Actions = _Actions.NORMAL):
        self.drag_enable = fixed
        self.pixmap_draw = QPixmap(source)  # 图片
        self.pixmap_raw = source  # 原始图片
        super().setPixmap(self.pixmap_draw)  # 添加pixmap
        self.setAction(action)  # 设置标志位
        pixmap_rect = self.pixmap_draw.size()
        rect = self.size()
        flag = pixmap_rect - rect
        if flag.width() > 0 or flag.height() > 0:
            scaled = rect.width() / pixmap_rect.width()
            scaled_h = rect.height() / pixmap_rect.height()
            scaled = min(scaled, scaled_h)

            height = int(scaled * pixmap_rect.height())
            width = int(rect.width() * scaled)
            x = (rect.width() - width) / 2
            y = (rect.height() - height) / 2
            rect = QRect(x, y, width, height)
            if point is not None:
                rect = QRect(point, rect.size())
        else:
            rect = self.pixmap_draw.rect()
            s = self.size() - self.pixmap_draw.size()
            rect = QRect(s.width() / 2, s.height() / 2,
                         rect.width(), rect.height())
            if point is not None:
                rect = QRect(point, self.pixmap_draw.size())

        if margins.isNull():
            self.pixmap_draw_rect = QRect(rect)  # 初始绘图区域
            self.pixmap_left_before = QRect(
                rect).topLeft()  # 初始绘画区域左上角, 控制拖拽移动的相关参数
            self.zoom_default_rect = QRect(rect)  # 光标缩放参数初始化
            self.default_rect = QRect(rect)  # 备份初始绘画区域
        else:
            self.pixmap_draw_rect = QRect(rect).marginsAdded(margins)  # 初始绘图区域
            self.pixmap_left_before = QRect(rect).marginsAdded(
                margins).topLeft()  # 初始绘画区域左上角, 控制拖拽移动的相关参数
            self.zoom_default_rect = QRect(
                rect).marginsAdded(margins)  # 光标缩放参数初始化
        self._restore = False
        self.update()

    def setPixmapVHCenter(self):
        self.pixmap_draw_rect.moveCenter(self.rect().center())
        self._moveAfterUpdateZoomParamters()

    # 计算视点缩放的相关参数(计算当前坐标和zoom_default_rect 左上角坐标的斜率与长度)
    def _calcAnglelength(self, left_top: QPoint, second: QPoint):  # 返回弧度, 长度
        pa_x = left_top.x()
        pa_y = left_top.y()
        pb_x = second.x()
        pb_y = second.y()
        x = pb_x - pa_x
        c = math.sqrt(math.pow(pb_y - pa_y, 2) + math.pow(pb_x - pa_x, 2))
        cosAgl = x / c
        angle = math.acos(cosAgl)
        return angle, c

    # 缩放后更新视点缩放相关参数
    def _zoomAfterupdateParameters(self, rect: QRect, current_point: QPoint = None):
        self.zoom_default_rect = QRect(rect)

    # 缩放前视点相关参数的计算
    def _zoomBeforeParametersCalculate(self, wheelEvent: QWheelEvent):
        left_top = self.zoom_default_rect.topLeft()
        current = wheelEvent.pos()
        self.topleft_angle, self.topleft_distance = self._calcAnglelength(
            left_top, current)

    # 图片拖拽后需更新视点缩放相关参数
    def _moveAfterUpdateZoomParamters(self):
        if self.viewpoint_zoom:
            self.zoom_default_rect = QRect(self.pixmap_draw_rect)

    # 图片缩放计算
    def _zoomCalculate(self, wheelEvent: QWheelEvent):
        # self.__pdfwidget.zoom_flag = -1  # 其他
        angle = wheelEvent.angleDelta() / 8
        if angle.y() < 0:  # 图像减小
            w, h = self.pixmap_draw_rect.width() * .95, self.pixmap_draw_rect.height() * .95
            self.pixmap_draw_rect.setSize(QSize(w, h))
            self._restore = False
            self.wheel_logs.append(False)
        else:  # 图像放大
            w, h = self.pixmap_draw_rect.width() * 1.05, self.pixmap_draw_rect.height() * 1.05
            flag_size = QSize(w, h) - self.pixmap_raw.size()
            if flag_size.width() >= 0 or flag_size.height() >= 0:
                self._restore = True
                self.wheel_logs.append(True)
            else:
                self.pixmap_draw_rect.setSize(QSize(w, h))

        zoom = self.pixmap_draw_rect.width() / self.zoom_default_rect.width()  # 缩放倍数
        if zoom >= 1:
            # self.pixmap_draw = self.pixmap_draw.scaled(w, h, transformMode=Qt.SmoothTransformation) # 更新图片
            pass
        if self.resize_auto_scaled:
            self.setFixedSize(QSize(w, h))
        if self.viewpoint_zoom:
            # 更新位置,保持视点不变
            new_left_x = self.zoom_default_rect.x() - self.topleft_distance * \
                         (zoom - 1) * math.cos(self.topleft_angle)
            new_left_y = self.zoom_default_rect.y() - self.topleft_distance * \
                         (zoom - 1) * math.sin(self.topleft_angle)
            self.pixmap_draw_rect.moveTo(QPoint(new_left_x, new_left_y))

    def enterEvent(self, event):
        self.grabKeyboard()
        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.releaseKeyboard()
        return super().leaveEvent(event)

    # override
    def drawPolicy(self, painter):
        painter.setPen(self.PEN)
        if self.action == _Actions.ZOOM or self.action == _Actions.MOVE or self.action == _Actions.NORMAL:
            painter.save()
            painter.setPen(QPen(QColor('#B7B7B7'), 2))  # 设置边框颜色
            painter.setRenderHint(QPainter.Antialiasing)
            if self._restore:
                logs: deque = self.wheel_logs
                if len(logs) <= 1:
                    self.addPixmap(self.pixmap_raw,
                                   self.pixmap_draw_rect.topLeft())
                else:
                    if all(logs):
                        pixmap = self.pixmap_draw
                        painter.drawPixmap(
                            self.pixmap_draw_rect, pixmap)  # 限制在rect
                        painter.drawRect(self.pixmap_draw_rect)
                    else:
                        self.addPixmap(self.pixmap_raw,
                                       self.pixmap_draw_rect.topLeft())
            else:
                pixmap = self.pixmap_draw.scaled(self.pixmap_draw_rect.size(), aspectRatioMode=Qt.KeepAspectRatio,
                                                 transformMode=Qt.SmoothTransformation)
                painter.drawPixmap(self.pixmap_draw_rect, pixmap)  # 限制在rect
                painter.drawRect(self.pixmap_draw_rect)
            painter.restore()

    # override
    def paintEvent(self, QPaintEvent):
        if self.edited:
            font = self.font()
            font.setPointSize(15)
            painter = QPainter()
            painter.begin(self)
            painter.setFont(font)
            self.drawPolicy(painter)
            painter.end()
        else:
            super().paintEvent(QPaintEvent)


class ImagesListLabel(QWidget):

    class LoadState(IntEnum):
        not_set = -1  # 初始状态
        fail = 0  # 请求失败
        success = 1  # 图片加载成功
        broken = 2  # 请求成功, 但返回无效图片

    class RoundList(object):

        def __init__(self, data: Union[List[str], List[bytes]] = None) -> None:
            if data:
                self._data = [(url, ImagesListLabel.LoadState.not_set)
                              for url in list(data)]
            else:
                self._data = []

            self._len = len(self._data)
            self._index = -1

        @property
        def current(self):
            return self._index

        def set_data(self, data: Union[List[str], List[bytes]]):
            self._data = [(url, ImagesListLabel.LoadState.not_set)
                          for url in list(data)]
            self._len = len(self._data)

        def length(self):
            return self._len

        def update(self, index, value):
            self._data[index] = value

        def next(self, index: int = None):
            if self._len:

                if index is not None:
                    self._index = index

                i = self._index + 1
                if i == self._len:
                    self._index = 0
                else:
                    self._index = i
                return self._data[self._index]

        def previous(self, index: int = None):
            if self._len:

                if index is not None:
                    self._index = index

                if self._index == -1 or self._index == 0:
                    self._index = self._len - 1
                else:
                    self._index -= 1
                return self._data[self._index]

        def reset(self):
            self._index = -1

    def save(self):
        self._keep = True
        if not self.pixmap().isNull():
            fmt = datetime.now().strftime('%Y%m%d%H%M%S')
            file, _ = QFileDialog.getSaveFileName(
                self, '保存图片', Path.cwd().joinpath(f'百舟打款助手_{fmt}.png').__str__(), '*.png;')
            if file:
                self.pixmap().save(file)
                Message.info(f'图片已保存: {file}', self)
        del self._keep

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self._window_size = QApplication.desktop().size()
        self._worker = kwargs.pop('worker', None)
        self._image_urls = self.RoundList()
        self._image_title = None
        self._max_show_size: QSize = QApplication.desktop().size() * 2 / 3
        self.mPos: QPoint = None

        self.setFixedSize(self._max_show_size)

        btn_style = '''
            QPushButton{border:none;background-color:transparent;color:white}
        '''

        btn_f = self.fontMetrics().width('abc') * 2
        self._next_btn = QPushButton(self)
        self._next_btn.setIcon(QIcon(':/imgs/前进面性(1).svg'))
        self._next_btn.setToolTip('下一张')
        self._next_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._next_btn.setShortcut(QKeySequence(Qt.Key_Right))

        self._previous_btn = QPushButton(self)
        self._previous_btn.setIcon(QIcon(':/imgs/后退面性(1).svg'))
        self._previous_btn.setToolTip('上一张')
        self._previous_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._previous_btn.setShortcut(QKeySequence(Qt.Key_Left))

        self._next_btn.setStyleSheet(btn_style)
        self._previous_btn.setStyleSheet(btn_style)

        self._loading_label = GifLabel(self)
        self._loading_label.setStyleSheet(
            'border:none;background-color: transparent')
        self._loading_label.setFixedWidth(btn_f * 2)

        self._text_label = QLabel(self)
        self._text_label.setStyleSheet(
            'border:none;font-family:微软雅黑;color:white')
        self._text_label.setAlignment(Qt.AlignCenter)

        self._title_label = QLabel(self)
        self._title_label.setStyleSheet(
            'border:none;font-family:微软雅黑;color:white')
        self._title_label.setAlignment(Qt.AlignLeft)
        self._title_label.setIndent(30)

        self._close_btn = QPushButton(self)
        self._close_btn.setIcon(QIcon(':/imgs/关闭.svg'))
        self._close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._close_btn.setStyleSheet(btn_style)
        self._close_btn.setToolTip('退出')
        self._close_btn.setShortcut('Esc')

        self._down_load = QPushButton(self)
        self._down_load.setIcon(QIcon(':/imgs/排序.svg'))
        self._down_load.setCursor(QCursor(Qt.PointingHandCursor))
        self._down_load.setStyleSheet(btn_style)
        self._down_load.setToolTip('保存图片')
        self._down_load.clicked.connect(self.save)

        self._next_btn.setFixedWidth(btn_f)
        self._previous_btn.setFixedWidth(btn_f)
        self._close_btn.setFixedWidth(btn_f)

        self._next_btn.show()
        self._previous_btn.show()

        self._next_btn.clicked.connect(lambda: self.next_image())
        self._previous_btn.clicked.connect(lambda: self.previous_image())
        self._close_btn.clicked.connect(self.close)

        self.setStyleSheet('border:none;background-color: rgb(50,50,50)')

        self._zoom_label = ZoomLabel(self)
        self._zoom_label.setFixedSize(self.width() - 80, self.height() - 30)
        self._zoom_label.move(40, 30)

        self.installEventFilter(self)

    def set_worker(self, worker: 'BackgroundWorker'):
        self._worker = worker

    def set_image_contents(self, imgs: Union[List[str], List[bytes]]):
        res = []
        j = -1
        for v in imgs:
            j += 1
            if not isinstance(v, (tuple, list)):
                res.append((v, j))
            else:
                res.append(v)
        self._image_urls = self.RoundList(res)

    def _reset(self):
        self._image_urls.reset()

    # ??
    def _get_image(self, url, index) -> None:

        async def _fetch_image(url, index):
            """
            异步加载图片
            """
            await asyncio.sleep(2)
            return url, index

        def call_back(ret):
            url, index = ret
            pixmap = QPixmap(url)
            self._image_urls.update(index, (pixmap, self.LoadState.success))
            print(index, url)

        def err_back(error):
            pass

        self._worker.add_coro(_fetch_image(url, index), call_back=call_back)

    def set_images_title(self, title: str):
        self._title_label.setText(title)

    def next_image(self, index: int = None):
        pic = self._image_urls.next(index)
        text_msg = f'{self._image_urls.current + 1}/{self._image_urls.length()}'
        if pic:
            data, state = pic
            if data[0]:
                if isinstance(data[0], str):
                    pixmap = QPixmap(data[0])
                    self._zoom_label.addPixmap(pixmap)
                    self._text_label.setText(text_msg)
                elif isinstance(data[0], bytes):
                    pixmap = QPixmap()
                    flag = pixmap.loadFromData(data[0])
                    if flag:
                        self._zoom_label.addPixmap(pixmap)
                    else:
                        self.fail_fetch()
                    self._text_label.setText(text_msg)

                elif isinstance(data[0], QPixmap):
                    try:
                        pixmap = QPixmap(data[0])
                        self._zoom_label.addPixmap(pixmap)
                        self._text_label.setText(text_msg)
                    except Exception as e:
                        print(e)
            else:
                self.fail_fetch()

    def previous_image(self, index: int = None):
        pic = self._image_urls.previous(index)
        text_msg = f'{self._image_urls.current + 1}/{self._image_urls.length()}'
        if pic:
            data, state = pic
            if data[0]:
                if isinstance(data[0], str):
                    pixmap = QPixmap(data[0])
                    self._zoom_label.addPixmap(pixmap)
                    self._text_label.setText(text_msg)
                elif isinstance(data[0], bytes):
                    pixmap = QPixmap()
                    flag = pixmap.loadFromData(data[0])
                    if flag:
                        self._zoom_label.addPixmap(pixmap)
                    else:
                        self.fail_fetch()
                    self._text_label.setText(text_msg)
                elif isinstance(data[0], QPixmap):
                    pixmap = QPixmap(data[0])
                    self._zoom_label.addPixmap(pixmap)
                    self._text_label.setText(text_msg)
            else:
                self.fail_fetch()

    def current_image(self):
        return self.pixmap()

    def pixmap(self) -> QPixmap:
        if isinstance(self._zoom_label.pixmap_raw, QPixmap):
            return self._zoom_label.pixmap_raw
        if self._zoom_label.pixmap_raw is not None:
            return QPixmap(self._zoom_label.pixmap_raw)
        return QPixmap()

    def fail_fetch(self):
        self._zoom_label.addPixmap(QPixmap(':/imgs/损坏(1).svg'), fixed=True)

    def show_label_list(self, index=None, size_scaled=2 / 3):
        self._reset()
        if index is not None:
            f = index - 1
        else:
            f = None
        self.next_image(f)
        size = self._window_size * size_scaled
        self.setFixedSize(size)
        self.show()

    def resizeEvent(self, a0) -> None:
        w, h = self.width(), self.height()
        bw = self._previous_btn.width()
        self._previous_btn.move(10, int(h / 2))

        self._next_btn.move(w - bw - 10, int(h / 2))
        self._next_btn.show()

        self._previous_btn.show()

        hc = w - bw - 10
        self._close_btn.move(hc, 5)
        self._close_btn.show()

        self._down_load.move(hc - 20, 5)
        self._down_load.show()

        hh = int(w - bw) / 2
        self._text_label.move(hh, 5)
        self._text_label.show()

        self._title_label.show()

        self._max_show_size = QSize(
            w - 24, h - self._text_label.fontMetrics().height() - 4)

        # 设置固定尺寸
        self._zoom_label.setFixedSize(w - 80, h - 30)
        self._zoom_label.move(40, 30)
        self._zoom_label.raise_()

        super().resizeEvent(a0)

    def mouseMoveEvent(self, ev: 'QMouseEvent') -> None:
        super().mousePressEvent(ev)
        if ev.buttons() == Qt.LeftButton and self.mPos:
            if self.mPos.y() <= 30:
                self.move(self.mapToGlobal(ev.pos() - self.mPos))

    def mousePressEvent(self, ev) -> None:
        super().mousePressEvent(ev)
        if ev.button() == Qt.LeftButton:
            self.mPos = ev.pos()
            if ev.pos().x() <= self.width() / 2:
                if ev.pos().y() > 30:
                    self._previous_btn.click()
            else:
                if ev.pos().y() > 30:
                    self._next_btn.click()

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a1.type() == QEvent.WindowDeactivate:
            if getattr(self, '_keep', None) is None:
                self.close()
        return QWidget.eventFilter(self, a0, a1)


class Images(ImagesListLabel):
    _persistence = None

    @classmethod
    def display(cls, pixmaps: Union[List[bytes], List[str]], title: str, target: QWidget = None, index=None):
        self = cls()
        cls._persistence = self
        self.set_images_title(title)
        self.set_image_contents(pixmaps)
        self.show_label_list(index)
