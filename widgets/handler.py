# -*- coding: utf-8 -*-
# @Time    : 2022/12/9 16:53
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : handler.py
# @Software: PyCharm

from lsp.utils import LspMethodId, LspContext

__lsp_msg_handlers__ = {}


def register_handler(lsp_serve_name: str, handler):
    __lsp_msg_handlers__.setdefault(lsp_serve_name, handler)


def handler_lsp_msg(app, msg: dict, lsp_serve_name: str):
    handler = __lsp_msg_handlers__.get(lsp_serve_name, None)
    if handler is not None:
        handler(app, msg, lsp_serve_name)
    else:
        print(f'{lsp_serve_name} msg handler not install!')


lsp_context = LspContext()


def base_lsp_handler(app, msg: dict, lsp_serve_name: str):
    from widgets.mainwidget import MainWidget
    from widgets.tabs import TabCodeWidget
    t = lsp_context.type
    convert = lsp_context.converter
    app: MainWidget
    current_tab: TabCodeWidget = app.current_tab()
    if msg['id'] == LspMethodId.textdocumentreferences_id:
        # obj = convert.gen_structure_attrs_fromdict(t.TextDocumentReferencesResponse)
        # s = obj(msg)
        print('lsp msg: ', msg)
        # print(s)
    elif msg['id'] == LspMethodId.initialize_id:
        print('init msg: ', msg)


register_handler('jedi-language-serve', base_lsp_handler)
