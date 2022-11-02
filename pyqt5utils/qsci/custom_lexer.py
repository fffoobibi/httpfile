from enum import IntEnum
from typing import Dict

from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QFont, QColor

__all__ = ('CustomStyles', 'CustomLexerCompat')

from abc import abstractmethod


class CustomStyles(IntEnum):

    @classmethod
    def generate_styles(cls) -> Dict[int, str]:
        dic = {}
        for k, v in cls.__members__.items():
            dic[v.value] = k
        return dic

    @classmethod
    def defaultColor(cls, style: int) -> QColor:
        raise NotImplementedError

    @classmethod
    def defaultPaper(cls, style: int) -> QColor:
        raise NotImplementedError

    @classmethod
    def defaultFont(cls, style: int, font: QFont) -> QFont:
        raise NotImplementedError


class CustomLexerCompat(QsciLexerCustom):
    styles_class: CustomStyles = CustomStyles
    language_desc: str = ''

    def __init__(self, parent):
        super().__init__(parent)
        self.__styles = self.styles_class.generate_styles()

    def language(self):
        return self.language_desc

    def description(self, style: int):
        return self.__styles.get(style, '')

    def defaultColor(self, style: int):
        color = self.styles_class.defaultColor(style)
        return color or super().defaultColor(style)

    def defaultPaper(self, style: int):
        paper_color = self.styles_class.defaultPaper(style)
        return paper_color or super().defaultPaper(style)

    def defaultFont(self, style: int):
        font: QFont = super().defaultFont(style)
        return self.styles_class.defaultFont(style, font)

    def styleText(self, start, end):
        raise NotImplementedError
