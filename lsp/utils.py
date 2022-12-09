# -*- coding: utf-8 -*-
# @Time    : 2022/12/9 8:38
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : utils.py
# @Software: PyCharm
from enum import IntEnum, auto
from typing import Tuple

from cached_property import cached_property
from lsprotocol import types
from lsprotocol.converters import get_converter


class LspContext(object):
    def __init__(self):
        self.client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @cached_property
    def type(self):
        return types

    @cached_property
    def method_id(self):
        return LspMethodId

    def body(self, obj) -> dict:
        return get_converter().unstructure(obj)

    @cached_property
    def converter(self):
        return get_converter()


class LspMethodId(IntEnum):
    initialize_id = 1
    textdocumentformatting_id = auto()
    textdocumentdocumenthighlight_id = auto()
    textdocumentdocumentsymbol_id = auto()
    textdocumentfolding_id = auto()
    textdocumentdocumentlink_id = auto()
    textdocumentdidsave_id = auto()
    textdocumentsignaturehelp_id = auto()
    textdocumentdidchange_id = auto()
    textdocumentdidopen_id = auto()
    textdocumentdidclose_id = auto()
    textdocumentinfer_id = auto()
    textdocumentcompletion_id = auto()
    textdocumenthover_id = auto()
    textdocumentreferences_id = auto()
    textdocumentrename_id = auto()
    textdocumentsyntaxcheck_id = auto()
