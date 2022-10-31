# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 11:16
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : comboboxs.py
# @Software: PyCharm
from collections import deque
from datetime import date, datetime
from typing import Any, List, Tuple

from PyQt5.QtCore import pyqtSignal, pyqtProperty, Qt, QDate, pyqtSlot, QSortFilterProxyModel, QSettings
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import QComboBox, QLineEdit, QPushButton, QCalendarWidget, QListWidget, QCompleter, QListView, \
    QListWidgetItem

from pyqt5utils.components.widgets import ComboLine
from pyqt5utils.components.widgets import CalendarDialog
from pyqt5utils.components.styles import Sh, StylesHelper


class SearchComBo(QComboBox):
    search_sig = pyqtSignal(list)

    def __init__(self, *a, **kw):
        super(SearchComBo, self).__init__(*a, **kw)
        self.setEditable(True)
        self.setLineEdit(ComboLine())
        self.setMaxVisibleItems(10)
        self.setView(QListWidget())
        self.log_list = deque()

        # 添加筛选器模型来筛选匹配项
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(
            Qt.CaseInsensitive)  # 大小写不敏感
        self.pFilterModel.setSourceModel(self.model())

        # 添加一个使用筛选器模型的QCompleter
        self.completer = QCompleter(self.pFilterModel, self)
        # 始终显示所有(过滤后的)补全结果
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)  # 不区分大小写
        popup_view = QListView()
        popup_view.setStyleSheet(Sh.historycombobox_listview_style)
        # popup_view.verticalScrollBar().setStyleSheet(Sh.history_v_scroll_style)
        popup_view.verticalScrollBar().setStyleSheet(Sh.vertical_scroll_style)
        self.completer.setPopup(popup_view)
        self.setCompleter(self.completer)

        # Qcombobox编辑栏文本变化时对应的槽函数
        self.lineEdit().textEdited.connect(self._text_changed)
        self.lineEdit().add_sig.connect(self._detect)
        self.completer.activated.connect(self.on_completer_activated)
        self.lineEdit().setClearButtonEnabled(False)

        self.setModel(self.view().model())

    def focusOutEvent(self, e) -> None:
        super().focusOutEvent(e)
        self.set_normal_style()

    def set_normal_style(self):
        self.setStyleSheet('''
              QComboBox {
              border:2px solid #ADC3F4;
              border-radius: 3px;
              height:26px;
              background:white;
              font-family: 微软雅黑;
              padding-left: 1px;}
              QComboBox:focus{
              border: 2px solid rgb(122,161,245)}
              QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
              }
              QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/箭头 下(1).svg')}
              QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}
              ''')

    def set_search_style(self):
        self.setStyleSheet('''
        QComboBox {
        border:2px solid #ADC3F4;
        border-radius: 3px;
        height:26px;
        background:white;
        font-family: 微软雅黑;
        padding-left: 1px;}
        QComboBox:focus{
        border: 2px solid rgb(122,161,245)}
        QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
        }
        QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/搜索小.svg')}
        QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}''')

    def _text_changed(self, value):
        self.pFilterModel.setFilterFixedString(value)
        if value:
            self.set_search_style()
        else:
            self.set_normal_style()

    def item_texts(self):
        return [self.itemText(i) for i in range(self.count())]

    @pyqtSlot(str)
    def _detect(self, value):
        if value not in self.item_texts():
            self.lineEdit().clear()

    # 当在Qcompleter列表选中候，下拉框项目列表选择相应的子项目
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.set_search_style()
            # self.activated[str].emit(self.itemText(index))

    # 在模型更改时，更新过滤器和补全器的模型
    def setModel(self, model):
        super(SearchComBo, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # 在模型列更改时，更新过滤器和补全器的模型列
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(SearchComBo, self).setModelColumn(column)

    # 回应回车按钮事件
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Enter & e.key() == Qt.Key_Return:
            text = self.currentText()
            # Qt.MatchExactly |
            index = self.findText(
                text, Qt.MatchCaseSensitive | Qt.MatchContains)
            if index > -1:
                self.setCurrentIndex(index)
            self.hidePopup()
            if index > -1:
                super(SearchComBo, self).keyPressEvent(e)
        else:
            super(SearchComBo, self).keyPressEvent(e)

    def current_data(self, user_role=Qt.UserRole):
        index = self.currentIndex()
        return self.itemData(index, user_role)

    def item_datas(self) -> List[Tuple[str, Any]]:
        res = []
        for i in range(self.count()):
            text, value = self.itemText(i), self.itemData(i, Qt.UserRole)
            res.append([text, value])
        return res

    def save_logs(self, file: QSettings, key='basic/historys'):
        dq = deque(maxlen=10)
        dq.extend(self.item_datas())
        file.setValue(key, list(dq))

    def add_datas(self, values):
        for text, value in values:
            self.addItem(text, value)


class SeachComBoEx(SearchComBo):
    click_signal = pyqtSignal()
    base_style_sheet = '''
            QComboBox {
                    border:1px solid gray;
                    border-radius: 0px;
                    font-family: 微软雅黑;
                    padding-left: 1px;}
                    QComboBox:focus{
                    border: 1px solid rgb(122,161,245)}
                    QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:26px;height:26px;border-left: none;
                    }
                    QComboBox::down-arrow{width:  12px;height: 12px;image: url(':/imgs/箭头 下(1).svg')}
                    QComboBox::down-arrow:on{width:  12px;height: 12px;image: url(':/imgs/箭头 右(1).svg')}
    '''

    class SortListWidgetItem(QListWidgetItem):
        def __init__(self, parent=None, index=0):
            super().__init__(parent)
            self.index = index

        def __lt__(self, other):
            return self.index < other.index

    def __init__(self, *a, **kw):
        super(SeachComBoEx, self).__init__(*a, **kw)
        self.lineEdit().setClearButtonEnabled(False)
        self.lineEdit().click_signal.connect(self.click_signal)
        self.currentIndexChanged.connect(self._sort)
        self._logs: dict = None
        self.setStyleSheet(self.base_style_sheet)
        StylesHelper.set_v_history_style(self.view())

    def load_logs(self, settings: QSettings, user: str):
        try:
            value = settings.value('basic/freqs', defaultValue=dict(), type=dict)
            self._logs = value.get(user, {})
        except:
            pass

    def save_logs(self, file: QSettings, user: str, key='basic/freqs'):
        try:
            view: QListWidget = self.view()
            value: dict = file.value(key, defaultValue=dict(), type=dict)
            users = list(value.keys())
            users.reverse()

            save_values = {}

            if len(users) > 5:
                for k in users[5:]:
                    value.pop(k, None)

            for count in range(self.count()):
                item = view.item(count)
                if item is not None:
                    save_values[item.text()] = item.index
            value[user] = save_values
            file.setValue(key, value)
        except:
            pass

    def _sort(self, index):
        view = self.view()
        item = view.item(index)
        if item:
            item.index += 1
            view.sortItems(Qt.DescendingOrder)

    def addItem(self, text: str, userData: Any) -> None:
        if self._logs:
            index = self._logs.get(text, 0)
        else:
            index = 0
        item = self.SortListWidgetItem(index=index)
        item.setText(text)
        item.setData(Qt.UserRole, userData)
        self.view().addItem(item)

    def set_place_holder(self, text: str):
        self.lineEdit().setPlaceholderText(text)

    def set_search_style(self):
        pass

    def set_normal_style(self):
        pass

    def add_datas(self, values: List[Tuple[str, Any]]):
        super(SeachComBoEx, self).add_datas(values)
        self._datas = values
        self.view().sortItems(Qt.DescendingOrder)

    def set_current_index_by_data(self, value):
        index = -1
        for i in range(self.count()):
            data = self.itemData(i, Qt.UserRole)
            if str(data) == str(value):
                index = i
                break
        if index > -1:
            self.setCurrentIndex(index)

    def set_current_index_by_value(self, value: str):
        index = -1
        for i in range(self.count()):
            data = self.itemData(i, Qt.UserRole)
            if self.itemText(i).lower().strip() == value.lower().strip():
                index = i
                break
        if index > -1:
            self.setCurrentIndex(index)


class DateComboBox(QComboBox):
    style_sheet = '''
        QComboBox {
            border:1px solid gray;
            border-radius: 5px;
            padding:3px 0px;
            background:white;
            font-family: 微软雅黑;
            padding-left: 2px;}
        QComboBox:focus{border: 1px solid rgb(122,161,245)}
        QComboBox::drop-down{subcontrol-origin: padding; subcontrol-position: center right; border-left: none;}/*  width:19px; height:18px; */
        /*QComboBox::down-arrow[can_clear="true"]{width:  14px;height: 14px;image: url()}*/
        /*QComboBox::down-arrow:on[can_clear="false"]{width:  14px;height: 14px;image: url(':/new/日历.svg')}*/
        QMenu{
            background:white;
            border:1px solid lightgray;
        }
        QMenu::item{
            padding:3px 20px;
            color:rgba(51,51,51,1);
            font-size:9pt;
            font-family:微软雅黑
        }
        QMenu::item:hover{background-color:rgb(236,236,237);}
        QMenu::item:selected{background-color:rgb(236,236,237);} 
    '''

    click_signal = pyqtSignal()

    class _Line(QLineEdit):
        click_signal = pyqtSignal()

        def mousePressEvent(self, a0) -> None:
            super().mousePressEvent(a0)
            if a0.button() == Qt.LeftButton:
                self.click_signal.emit()

    def clear(self):
        self._current_value = None
        self._line.clear()
        self.can_clear = False

    @pyqtProperty(bool)
    def can_clear(self):
        return self._can_clear

    @can_clear.setter
    def can_clear(self, v):
        self._can_clear = v
        # self.style().polish(self)
        rw, rh = self.width(), self.height()
        self.clear_btn.setFixedSize(rh - 6, rh - 6)
        w, h = self.clear_btn.width(), self.clear_btn.height()
        self.clear_btn.move(self.width() - w - 4, (self.height() - h) / 2)
        self.clear_btn.raise_()
        if v == True:
            self.clear_btn.setIcon(QIcon(':/new/日历-删除.svg'))
        else:
            self.clear_btn.setIcon(QIcon(':/new/日历.svg'))
        self.clear_btn.show()

    def _clear_slot(self):
        if self._current_value is not None:
            self.can_clear = not self.can_clear
            self._line.clear()
            self._current_value = None

    def __init__(self, *a, **kw):
        super(DateComboBox, self).__init__(*a, **kw)
        self._fmt = '%Y-%m-%d'
        self._current_value = None
        self._line = self._Line()
        self._line.click_signal.connect(self.click_signal)
        self._line.setReadOnly(True)
        self.setLineEdit(self._line)
        self.click_signal.connect(self._select_date)
        self.set_place_holder('请选择日期')
        self.clear_btn = QPushButton(self)
        self.clear_btn.setFixedSize(15, 15)
        self.clear_btn.setStyleSheet('QPushButton{border:none;background:transparent}')
        self.clear_btn.setIcon(QIcon(':/new/日历-删除.svg'))
        self.clear_btn.hide()
        self.clear_btn.clicked.connect(self._clear_slot)
        self.can_clear = False
        self.setStyleSheet(self.style_sheet)

    @property
    def current_value(self) -> date:
        return self._current_value

    @property
    def current_text(self) -> str:
        return self._line.text().strip()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        super().resizeEvent(a0)
        w, h = self.clear_btn.width(), self.clear_btn.height()
        self.clear_btn.move(self.width() - w - 4, (self.height() - h) / 2)

    def set_place_holder(self, st):
        self._line.setPlaceholderText(st)
        self.setMinimumWidth(self._line.fontMetrics().width(st) + 70)

    def set_format(self, fmt):
        self._fmt = fmt

    def _select_date(self):
        self._date_dialog = CalendarDialog()
        self._date_dialog.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self._date_dialog.calendar.setSelectedDate(self._current_value or QDate.currentDate())
        self._date_dialog.calendar.setMaximumDate(datetime.now().date())
        self._date_dialog.calendar.setMouseTracking(True)
        self._date_dialog.ok_signal.connect(self._set_value)
        self._date_dialog.pop(self)

    @pyqtSlot(date)
    def _set_value(self, value: date):
        self._current_value = value
        self.setCurrentText(value.strftime(self._fmt))
        self.can_clear = True
