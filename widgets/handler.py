# -*- coding: utf-8 -*-
# @Time    : 2022/12/9 16:53
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : handler.py
# @Software: PyCharm
from typing import List

from lsp.utils import LspMethodId, lsp_context

__lsp_msg_handlers__ = {}


def register_handler(lsp_serve_name: str, handler):
    __lsp_msg_handlers__.setdefault(lsp_serve_name, handler)


def handler_lsp_msg(app, msg: dict, lsp_serve_name: str, file_path: str):
    handler = __lsp_msg_handlers__.get(lsp_serve_name, None)
    if handler is not None:
        handler(app, msg, lsp_serve_name, file_path)
    else:
        print(f'{lsp_serve_name} msg handler not install!')


def base_lsp_handler(app, msg: dict, lsp_serve_name: str, file_path: str):
    from widgets.mainwidget import MainWidget
    from widgets.tabs import TabCodeWidget
    app: MainWidget
    current_tab: TabCodeWidget = app.current_tab()
    current_file_path = app.current_file_path()
    msg_id = msg.get('id', None)
    if msg_id == LspMethodId.initialize_id:
        app.register_lsp_serve_capacities(lsp_serve_name, msg['result']['capabilities'])
    if current_tab and current_file_path == file_path:
        print('get msg ', msg)
        if msg_id:
            if msg_id == LspMethodId.initialize_id:
                print('init msg: ', msg)
            elif msg_id == LspMethodId.textdocumentreferences_id:
                rs = []
                for result in msg['result'] or []:
                    rs.append(lsp_context.converter.structure(result, lsp_context.type.Location))
                current_tab.lsp_render.render_references(rs)

            elif msg_id == LspMethodId.textdocumentdocumenthighlight_id:
                print('hiligh: ', msg)
            elif msg['id'] == LspMethodId.textdocumentdocumentsymbol_id:
                print('symbols: ')
                import pprint
                pprint.pprint(msg)
            elif msg_id == LspMethodId.textdocumentcolor_id:
                print('colors: ')
                import pprint
                pprint.pprint(msg)
            elif msg_id == LspMethodId.textdocumentcompletion_id:
                print('complete')
                import pprint
                print(msg)
        # notification
        else:
            notification_method = msg.get('method', None)
            if notification_method == lsp_context.type.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS:
                params = msg['params']
                uri = params['uri']
                diagnostics = params['diagnostics']
                obj = lsp_context.converter.structure(diagnostics, List[lsp_context.type.Diagnostic])
                current_tab.lsp_render.render_diagnostics(uri, obj)


register_handler('jedi-language-serve', base_lsp_handler)
register_handler('pylsp', base_lsp_handler)
register_handler('vscode-json-language-server', base_lsp_handler)
