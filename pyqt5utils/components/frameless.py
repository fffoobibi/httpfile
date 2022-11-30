import weakref

from types import MethodType

from PyQt5.QtCore import Qt, QRect, QSize, QPropertyAnimation, pyqtSignal, QPoint
from PyQt5.QtGui import QPalette, QIcon, QColor, QFont, QPainter, QEnterEvent, QPen
from PyQt5.QtWidgets import QDialog, QPushButton, QWidget, QVBoxLayout, QApplication, QLabel, QSpacerItem, QHBoxLayout, \
    QSizePolicy

__all__ = ('TitleWidget',)


class _TitleBar(QWidget):
    # 窗口最小化信号
    windowMinimumed = pyqtSignal()
    # 窗口最大化信号
    windowMaximumed = pyqtSignal()
    # 窗口还原信号
    windowNormaled = pyqtSignal()
    # 窗口关闭信号
    windowClosed = pyqtSignal()
    # 窗口移动
    windowMoved = pyqtSignal(QPoint)
    # 鼠标点击
    mPressed = pyqtSignal()

    _styleSheet = """
        /*标题栏*/
        /*最小化最大化关闭按钮通用默认背景*/
        #buttonMinimum,#buttonMaximum,#buttonClose {
            border: none;
            background-color:transparent

        }
        /*悬停*/
        #buttonMinimum:hover,#buttonMaximum:hover {
            color: white;
        }
        #buttonClose:hover {
            color: white;
        }
        /*鼠标按下不放*/
        #buttonMinimum:pressed,#buttonMaximum:pressed {
            background-color: Firebrick;
        }
        #buttonClose:pressed {
            color: white;
            background-color: Firebrick;
        }
    """

    def __init__(self, *args, **kwargs):
        super(_TitleBar, self).__init__(*args, **kwargs)
        # 支持qss设置背景
        self.setAttribute(Qt.WA_StyledBackground, True)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.mPos = None
        self.iconSize = 20  # 图标的默认大小
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        # 布局
        layout = QHBoxLayout(self, spacing=0)
        layout.setContentsMargins(10, 0, 0, 0)
        # 窗口图标
        self.iconLabel = QLabel(self)
        layout.addWidget(self.iconLabel)
        # 窗口标题
        self.titleLabel = QLabel(self)
        self.titleLabel.setAttribute(
            Qt.WA_TransparentForMouseEvents, True)  # 鼠标穿透,当前控件及其子控件均不响应鼠标事件
        self.titleLabel.setMargin(2)
        self.titleLabel.setFont(QFont('微软雅黑'))
        layout.addWidget(self.titleLabel)
        # 中间伸缩条
        layout.addSpacerItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # 利用Webdings字体来显示图标
        # font = self.font() or QFont()
        font = QFont('Webdings')
        # 最小化按钮
        self.buttonMinimum = QPushButton(
            '0', self, clicked=self.windowMinimumed.emit, font=font, objectName='buttonMinimum')
        layout.addWidget(self.buttonMinimum)
        # 最大化/还原按钮
        self.buttonMaximum = QPushButton(
            '1', self, clicked=self.showMaximized, font=font, objectName='buttonMaximum')
        layout.addWidget(self.buttonMaximum)
        # 关闭按钮
        self.buttonClose = QPushButton(
            'r', self, clicked=self.windowClosed.emit, font=font, objectName='buttonClose')
        layout.addWidget(self.buttonClose)
        # 初始高度
        self.setHeight()
        self.setStyleSheet(self._styleSheet)

        self.windowMinimumed.connect(self.mPressed)
        self.windowClosed.connect(self.mPressed)

    def addTitleWidget(self, widget, stretch=0, *, autoheight=True):
        lay: QHBoxLayout = self.layout()
        lay.insertWidget(3, widget, stretch=stretch)
        if autoheight:
            widget.setFixedHeight(self.height())
            widget.setMinimumWidth(self.height())

    def addLeftTitleWidget(self, widget, stretch=0, *, autoheight=True):
        lay: QHBoxLayout = self.layout()
        lay.insertWidget(2, widget, stretch=stretch)
        if autoheight:
            widget.setFixedHeight(self.height())
            widget.setMinimumWidth(self.height())

    def showMaximized(self):
        if self.buttonMaximum.text() == '1':
            # 最大化
            self.buttonMaximum.setText('2')
            self.windowMaximumed.emit()
        else:  # 还原
            self.buttonMaximum.setText('1')
            self.windowNormaled.emit()

    def setHeight(self, height=38):
        """设置标题栏高度"""
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        # 设置右边按钮的大小
        self.buttonMinimum.setMinimumSize(height, height)
        self.buttonMinimum.setMaximumSize(height, height)
        self.buttonMaximum.setMinimumSize(height, height)
        self.buttonMaximum.setMaximumSize(height, height)
        self.buttonClose.setMinimumSize(height, height)
        self.buttonClose.setMaximumSize(height, height)

    def setTitle(self, title):
        """设置标题"""
        self.titleLabel.setText(f'<b>{title}</b>')

    def setBarColor(self, color):
        palette = QPalette(self.palette())
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
        self.update()

    def setTitleStyle(self, styleSheet: str):
        self.titleLabel.setStyleSheet(styleSheet)

    def setIcon(self, icon):
        """设置图标"""
        self.iconLabel.setPixmap(icon.pixmap(self.iconSize, self.iconSize))

    def setIconSize(self, size):
        """设置图标大小"""
        self.iconSize = size

    def enterEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super(_TitleBar, self).enterEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(_TitleBar, self).mouseDoubleClickEvent(event)
        # self.showMaximized()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.mPressed.emit()
        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.mPos:
            self.windowMoved.emit(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()


# 枚举左上右下以及四个定点
Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)


class _FramelessWindow(QWidget):
    # 四周边距
    Margins = 2

    CurSorMargins = 5

    windowMoved = pyqtSignal(QPoint)

    def __init__(self, *args, **kwargs):
        super(_FramelessWindow, self).__init__(*args, **kwargs)
        self._auto_resize = False
        self._pressed = False

        self.nestle_enable = False  # 贴靠
        self.moved = False  # flag

        self.border_color = Qt.lightGray

        self.Direction = None
        self.setMouseTracking(True)
        # 背景透明
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 无边框
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowMinimizeButtonHint)  # 隐藏边框
        # 鼠标跟踪
        self.setMouseTracking(True)
        # 布局
        layout = QVBoxLayout(self)
        layout.setSpacing(3)  # old 0
        # 预留边界用于实现无边框窗口调整大小
        layout.setContentsMargins(
            self.Margins, self.Margins, self.Margins, self.Margins)
        # 标题栏
        self.titleBar = _TitleBar(self)
        layout.addWidget(self.titleBar)
        # 信号槽
        self.titleBar.windowMinimumed.connect(self.showMinimized)
        self.titleBar.windowMaximumed.connect(self.showMaximized)
        self.titleBar.windowNormaled.connect(self.showNormal)
        self.titleBar.windowClosed.connect(self.close)
        self.titleBar.windowMoved.connect(self.move)
        self.windowTitleChanged.connect(self.titleBar.setTitle)
        self.windowIconChanged.connect(self.titleBar.setIcon)

    def set_auto_resize(self, value: bool):
        self._auto_resize = value

    def addTitleWidget(self, widget, stretch=0, autoheight=True):
        self.titleBar.addTitleWidget(widget, stretch, autoheight=autoheight)

    def addLeftTitleWidget(self, widget, stretch=0, autoheight=True):
        self.titleBar.addLeftTitleWidget(
            widget, stretch, autoheight=autoheight)

    def setTitleBarHeight(self, height=38):
        """设置标题栏高度"""
        self.titleBar.setHeight(height)

    def setBackgroundColor(self, color):
        palatte = QPalette(self.palette())
        palatte.setColor(QPalette.Background, QColor(color))
        self.setAutoFillBackground(True)
        self.setPalette(palatte)
        self.update()

    def setTitleBarColor(self, color):
        palatte = QPalette(self.titleBar.palette())
        palatte.setColor(QPalette.Background, QColor(color))
        # palatte.setColor(QPalette.Foreground, Qt.red)
        self.titleBar.setAutoFillBackground(True)
        self.titleBar.setPalette(palatte)
        self.titleBar.update()

    def setTitleTextColor(self, color):
        label = self.titleBar.titleLabel
        palatte = QPalette(label.palette())
        palatte.setColor(QPalette.Foreground, QColor(color))
        # label.setAutoFillBackground(True)
        label.setPalette(palatte)
        label.update()

    def barColor(self) -> QColor:
        palatte = self.titleBar.palette()
        return palatte.color(QPalette.Background)

    def barHeight(self):
        return self.titleBar.height() + self.Margins * 2

    def setIconSize(self, size):
        """设置图标的大小"""
        self.titleBar.setIconSize(size)

    def setWidget(self, widget, set_bkg: bool = True):
        """设置自己的控件"""
        if hasattr(self, '_widget'):
            return
        self._widget = widget
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        if set_bkg:
            self._widget.setAutoFillBackground(True)
            palette = self._widget.palette()
            palette.setColor(palette.Window, QColor(240, 240, 240))
            self._widget.setPalette(palette)
        self._widget.installEventFilter(self)
        self.layout().addWidget(self._widget)

    def move(self, pos):
        if self.windowState() == Qt.WindowMaximized or self.windowState() == Qt.WindowFullScreen:
            # 最大化或者全屏则不允许移动
            return
        super(_FramelessWindow, self).move(pos)
        self.windowMoved.emit(pos)

    def showMaximized(self):
        """最大化,要去除上下左右边界,如果不去除则边框地方会有空隙"""
        super(_FramelessWindow, self).showMaximized()
        self.layout().setContentsMargins(0, 0, 0, 0)

    def showNormal(self):
        """还原,要保留上下左右边界,否则没有边框无法调整"""
        super(_FramelessWindow, self).showNormal()
        self.layout().setContentsMargins(
            self.Margins, self.Margins, self.Margins, self.Margins)

    def eventFilter(self, obj, event):
        """事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式"""
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(_FramelessWindow, self).eventFilter(obj, event)

    def paintEvent(self, event):
        """由于是全透明背景窗口,重绘事件中绘制透明度为1的难以发现的边框,用于调整窗口大小"""
        super(_FramelessWindow, self).paintEvent(event)
        painter = QPainter(self)
        bar = self.barColor()
        height = self.barHeight()
        if not self.titleBar.isHidden():
            painter.setPen(self.barColor())
            # painter.setPen(self.border_color)
            painter.fillRect(QRect(0, 0, self.width(), height), bar)

            painter.setPen(QPen(QColor(self.border_color), 1))
            painter.drawRect(QRect(0, height, self.width() -
                                   1, self.height() - height - 1))
            # 绘制边框
            painter.setPen(bar)
            painter.drawLine(0, height, self.width(), height)

        else:
            painter.setPen(QColor(self.border_color))
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        super(_FramelessWindow, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._mpos = event.pos()
            self._pressed = True

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        super(_FramelessWindow, self).mouseReleaseEvent(event)
        self._pressed = False
        self.Direction = None

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super(_FramelessWindow, self).mouseMoveEvent(event)
        pos = event.pos()
        xPos, yPos = pos.x(), pos.y()
        if self._auto_resize:
            wm, hm = self.width() - self.CurSorMargins, self.height() - self.CurSorMargins
            if self.isMaximized() or self.isFullScreen():
                self.Direction = None
                self.setCursor(Qt.ArrowCursor)
                return
            if event.buttons() == Qt.LeftButton and self._pressed:
                self._resizeWidget(pos)
                return
            if xPos <= self.CurSorMargins and yPos <= self.CurSorMargins:
                # 左上角
                self.Direction = LeftTop
                self.setCursor(Qt.SizeFDiagCursor)
            elif wm <= xPos <= self.width() and hm <= yPos <= self.height():
                # 右下角
                self.Direction = RightBottom
                self.setCursor(Qt.SizeFDiagCursor)
            elif wm <= xPos and yPos <= self.CurSorMargins:
                # 右上角
                self.Direction = RightTop
                self.setCursor(Qt.SizeBDiagCursor)
            elif xPos <= self.CurSorMargins and hm <= yPos:
                # 左下角
                self.Direction = LeftBottom
                self.setCursor(Qt.SizeBDiagCursor)
            elif 0 <= xPos <= self.CurSorMargins and self.CurSorMargins <= yPos <= hm:
                # 左边
                self.Direction = Left
                self.setCursor(Qt.SizeHorCursor)
            elif wm <= xPos <= self.width() and self.CurSorMargins <= yPos <= hm:
                # 右边
                self.Direction = Right
                self.setCursor(Qt.SizeHorCursor)
            elif self.CurSorMargins <= xPos <= wm and 0 <= yPos <= self.CurSorMargins:
                # 上面
                self.Direction = Top
                self.setCursor(Qt.SizeVerCursor)
            elif self.CurSorMargins <= xPos <= wm and hm <= yPos <= self.height():
                # 下面
                self.Direction = Bottom
                self.setCursor(Qt.SizeVerCursor)

    def _resizeWidget(self, pos):
        """调整窗口大小"""
        if self.Direction == None:
            return
        if not self._auto_resize:
            return
        mpos = pos - self._mpos
        xPos, yPos = mpos.x(), mpos.y()
        geometry = self.geometry()
        x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
        if self.Direction == LeftTop:  # 左上角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
        elif self.Direction == RightBottom:  # 右下角
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
        elif self.Direction == RightTop:  # 右上角
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos.setX(pos.x())
        elif self.Direction == LeftBottom:  # 左下角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos.setY(pos.y())
        elif self.Direction == Left:  # 左边
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return
        elif self.Direction == Right:  # 右边
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            else:
                return
        elif self.Direction == Top:  # 上面
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return
        elif self.Direction == Bottom:  # 下面
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
            else:
                return
        self.setGeometry(x, y, w, h)

    @property
    def window_size(self) -> QSize:
        return QApplication.desktop().size()

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.nestle_enable:
            self._hide_or_show('show', event)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self.nestle_enable:
            self._hide_or_show('hide', event)

    def _hide_or_show(self, mode, event):
        pos = self.frameGeometry().topLeft()
        size = self.window_size
        pos = self.frameGeometry().topLeft()
        if mode == 'show' and self.moved:
            if pos.x() + self.width() >= size.width():  # 右侧显示
                self._start_animation(size.width() - self.width() + 2, pos.y())
                event.accept()
                self.moved = False
            elif pos.x() <= 0:  # 左侧显示
                self._start_animation(0, pos.y())
                event.accept()
                self.moved = False
            elif pos.y() <= 0:  # 顶层显示
                self._start_animation(pos.x(), 0)
                event.accept()
                self.moved = False
        elif mode == 'hide':
            if pos.x() + self.width() >= size.width():  # 右侧隐藏
                self._start_animation(size.width() - 2, pos.y())
                event.accept()
                self.moved = True
            elif pos.x() <= 2:  # 左侧隐藏
                self._start_animation(2 - self.width() + 1, pos.y())
                event.accept()
                self.moved = True
            elif pos.y() <= 2:  # 顶层隐藏
                self._start_animation(pos.x(), 2 - self.height())
                event.accept()
                self.moved = True

    def _start_animation(self, width, height):
        animation = QPropertyAnimation(self, b"geometry", self)
        startpos = self.geometry()
        animation.setDuration(200)
        newpos = QRect(width, height, startpos.width(), startpos.height())
        animation.setEndValue(newpos)
        animation.start()


class TitleWidget(_FramelessWindow):
    windowMoved = pyqtSignal(QPoint)
    _instances_ = weakref.WeakValueDictionary()
    _configs_ = dict(
        bar_height=None,
        back_ground_color=None,
        bar_color=QColor('#426BDD'),
        border_color=Qt.transparent,
        text_color=Qt.red,
        auto_resize=False,
        nestle_enable=False,
        icon=QIcon(),
        icon_size=16,
        button_text_color=Qt.white,
        button_hover_color=QColor(109, 139, 222),
        button_hide_policy=None)

    @property
    def content_widget(self) -> QWidget:
        return self._widget

    @classmethod
    def config(cls, **config_params):
        cls._configs_.update(**config_params)
        for k in cls._instances_:
            cls._instances_[k].set_style(config_params)

    @classmethod
    def config_from_json(cls, json_file: str, encoding='utf8'):
        import json
        cls.config(json.load(open(json_file, mode='r', encoding=encoding)))

    def _init_attr_(self, **kw):
        for k in self._configs_:
            if k != 'bar_height':
                if k != 'icon':
                    setattr(self, k, kw.get(k) or self._configs_.get(k))
                else:
                    icon = QIcon(kw.get(k) or self._configs_.get(k))
                    setattr(self, k, icon)
            else:
                bar_height = self.titleBar.titleLabel.fontMetrics().height() + 10
                setattr(self, k, kw.get(k) or (self._configs_.get(k) or bar_height))

    def __init__(self, title: str, widget: QWidget = None, parent: QWidget = None, **kw):
        super().__init__(parent)
        self.kw = kw
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowTitle(title) if title else None
        self.set_style()
        self.set_content_Widget(widget) if widget is not None else None
        self._instances_[id(self)] = self

    @classmethod
    def instance(cls, id_value):
        return cls._instances_.get(id_value)

    def set_style(self, kw_params: dict = None):
        if kw_params is not None:
            self.kw.update(**kw_params)
        self._init_attr_(**self.kw)
        self.setIconSize(self.icon_size)
        self.setWindowIcon(self.icon)
        self.set_auto_resize(self.auto_resize)
        self.setTitleBarColor(self.bar_color)
        self.setTextColor(self.text_color)
        self.setButtonStyle(self.button_text_color, self.button_hover_color, self.button_hide_policy)
        self.setTitleBarHeight(self.bar_height)
        if self.back_ground_color is not None:
            self.setBackgroundColor(self.back_ground_color)

    def hide_title_bar(self):
        self.titleBar.hide()

    def set_content_Widget(self, target: QWidget, set_bkg=True):
        target.root = self
        self.setWidget(target, set_bkg)
        self.override_widget()

    def setTextColor(self, color):
        self.titleBar.titleLabel.setStyleSheet(
            f'border:none;color: {QColor(color).name()}')

        s = '''
            QPushButton{color:  %s, border:none;background:transparent}
            QPushButton:hover{color: black;border:none}
        ''' % QColor(color).name()
        self.titleBar.buttonClose.setStyleSheet(s)
        self.titleBar.buttonMinimum.setStyleSheet(s)
        self.titleBar.buttonMaximum.setStyleSheet(s)

    def setButtonStyle(self, text_color, hover_color, hide_policy: set = None):
        style = '''
        QPushButton{color: %s; font-family: Webdings}
        QPushButton:hover{background-color: %s;border-radius:0px}
        ''' % (QColor(text_color).name(), QColor(hover_color).name())
        self.titleBar.buttonMinimum.setStyleSheet(style)
        self.titleBar.buttonMaximum.setStyleSheet(style)
        self.titleBar.buttonClose.setStyleSheet(style)
        # title_height = self.titleBar.titleLabel.fontMetrics().height() + 10
        if hide_policy is not None:
            for e in hide_policy:
                if e == 'min':
                    self.titleBar.buttonMinimum.hide()
                elif e == 'max':
                    self.titleBar.buttonMaximum.hide()
                elif e == 'close':
                    self.titleBar.buttonClose.hide()
        else:
            self.titleBar.buttonMinimum.show()
            self.titleBar.buttonMaximum.show()
            self.titleBar.buttonClose.show()

    def hide_titlebar_all(self):
        self.titleBar.buttonMinimum.hide()
        self.titleBar.buttonClose.hide()
        self.titleBar.buttonMaximum.hide()

    def hide_btns(self, close_btn=False, min_btn=False, max_btn=False):
        self.titleBar.buttonClose.setHidden(close_btn)
        self.titleBar.buttonMinimum.setHidden(min_btn)
        self.titleBar.buttonMaximum.setHidden(max_btn)

    def close_btn(self, style: str):
        f = QFont('Webdings')
        btn = QPushButton('r')
        btn.setFont(f)
        btn.clicked.connect(self.close)
        btn.setStyleSheet(style)
        return btn

    def min_btn(self, style):
        f = QFont('Webdings')
        btn = QPushButton('0')
        btn.setFont(f)
        btn.clicked.connect(self.showMinimized)
        btn.setStyleSheet(style)
        return btn

    def max_btn(self, style):
        f = QFont('Webdings')
        btn = QPushButton('1')
        btn.setFont(f)
        btn.clicked.connect(self.showMaximized)
        btn.setStyleSheet(style)
        return btn

    def override_widget(self):
        def move(this, point):
            if this.root:
                this.root.move(point)

        def show(this) -> None:
            if this.root:
                this.root.raise_()
                this.root.show()
                this.root.showNormal()

        def setWindowTitle(this, a0: str):
            self._widget.__class__.setWindowTitle(this, a0)
            if this.root:
                this.root.setWindowTitle(a0)

        def showNormal(this):
            if this.root:
                this.root.showNormal()

        def raise_(this) -> None:
            if this.root:
                this.root.raise_()

        def close(this):
            if this.root:
                try:
                    this.root.close()
                except Exception:
                    pass
                try:
                    if getattr(this, 'before_close', None) is not None:
                        this.before_close()
                except Exception:
                    pass

        def exec_(this):
            if this.root:
                this.root.show()
                QDialog.exec_(self._widget)

        self._widget.move = MethodType(move, self._widget)
        self._widget.show = MethodType(show, self._widget)
        self._widget.raise_ = MethodType(raise_, self._widget)
        self._widget.close = MethodType(close, self._widget)
        self._widget.exec_ = MethodType(exec_, self._widget)
        self._widget.showNormal = MethodType(showNormal, self._widget)
        self._widget.setWindowTitle = MethodType(setWindowTitle, self._widget)

    def closeEvent(self, a0) -> None:
        super().closeEvent(a0)
        self._widget.close()

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
