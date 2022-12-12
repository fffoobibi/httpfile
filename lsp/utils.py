# -*- coding: utf-8 -*-
# @Time    : 2022/12/9 8:38
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : utils.py
# @Software: PyCharm
from enum import IntEnum, auto, Enum
from typing import Tuple, Union

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

    @cached_property
    def token(self):
        return LspToken

    def body(self, obj, method_name: str = None) -> Union[dict, tuple]:
        obj = get_converter().unstructure(obj)
        if method_name is not None:
            return obj, method_name
        return obj

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
    textdocumentsignaturehelp_id = auto()
    textdocumentinfer_id = auto()
    textdocumentcompletion_id = auto()
    textdocumenthover_id = auto()
    textdocumentreferences_id = auto()
    textdocumentrename_id = auto()
    textdocumentcolor_id = auto()
    textdocumentdiagnosticrequest_id = auto()

    # notification
    textdocumentdidchange_id = auto()
    textdocumentdidopen_id = auto()
    textdocumentdidclose_id = auto()
    textdocumentdidsave_id = auto()
    textdocumentpublishdiagnostics_id = auto()


class LspToken(str, Enum):
    initialize_token = 'initialize_token'
    formatting_token = 'formatting_token'
    diagnosticrequest_token = 'diagnosticrequest_token'


lsp_context = LspContext()
