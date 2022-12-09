# -*- coding: utf-8 -*-
# @Time    : 2022/12/8 10:26
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : lsp_interface.py
# @Software: PyCharm
import inspect
import types
from typing import Tuple

from cached_property import cached_property
from lsprotocol.types import ClientCapabilities, InitializeParamsClientInfoType

from lsp.interface import LSPAppMixIn
from lsp.utils import LspContext

from pyqt5utils.workers import WorkerManager


class ILanguageServe(object):
    def capacities(self) -> int:
        return 0

    def lsp_serve_name(self) -> str:
        raise NotImplementedError

    def lsp_init_kw(self) -> dict:
        raise NotImplementedError

    def clientCapacities(self) -> ClientCapabilities:
        raise NotImplementedError

    def on_initialize(self):
        raise NotImplementedError

    def on_textdocumentformatting(self):
        raise NotImplementedError

    def on_textdocumentdocumenthighlight(self):
        raise NotImplementedError

    def on_textdocumentdocumentsymbol(self):
        raise NotImplementedError

    def on_textdocumentfolding(self):
        raise NotImplementedError

    def on_textdocumentdocumentlink(self):
        raise NotImplementedError

    def on_textdocumentdidsave(self):
        raise NotImplementedError

    def on_textdocumentsignaturehelp(self):
        raise NotImplementedError

    def on_textdocumentdidchange(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentdidopen(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentdidclose(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentinfer(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentcompletion_(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumenthover(self, word: str, line: int, col: int):
        raise NotImplementedError

    def on_textdocumentreferences(self, word: str, line: int, col: int):
        raise NotImplementedError

    def on_textdocumentrename(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentsyntaxcheck(self, word: str, line, col):
        raise NotImplementedError


class LanguageServerMixIn(ILanguageServe):
    language_client_class: 'TCPLanguageClient'

    language_mask = 0
    rename_flag = 1
    infer_flag = 1 << 1
    completion_flag = 1 << 2
    hover_flag = 1 << 3
    ref_flag = 1 << 4
    syntax_flag = 1 << 5

    app: LSPAppMixIn  # type hint

    @cached_property
    def lsp_worker(self):
        return WorkerManager().get('lsp-worker')

    def _client(self):
        serve_name, init_kw = self.client_init_params()
        return self.language_client_class(serve_name, **init_kw)

    def support_enabled(self, flags: int):
        self.language_mask |= flags

    def supported(self, flag: int):
        return self.language_mask & flag

    def support_disabled(self, flag: int):
        self.language_mask &= ~flag

    def set_up_from_obj(self, obj):
        clz = obj.__class__
        for k, v in clz.__dict__.items():
            if inspect.isfunction(v) and (v.__name__.startswith('on_') or v.__name__ in ['capacities',
                                                                                         'lsp_init_kw',
                                                                                         'clientCapacities',
                                                                                         'lsp_serve_name']):
                bound_method = types.MethodType(v, self)
                setattr(self, k, bound_method)

    #### language server protocol ###

    def client_init_params(self) -> Tuple:
        params = self.lsp_serve_name(), self.lsp_init_kw()
        return params

    def register_to_app(self, main_app: LSPAppMixIn):
        print('register lsp services', self._client)
        main_app.register_lsp_serve_params(self.client_init_params(), self._client)
        self.app = main_app

    def capacities(self) -> int:
        return 0

    def client_info(self) -> InitializeParamsClientInfoType:
        return InitializeParamsClientInfoType(
            name='fxk-editor',
            version='1.0.0'
        )

    # decorator
    def send_to_language_serve(method):

        def wrapper(self, *a, **kw):
            serve_name = self.lsp_serve_name()

            async def _send(body):
                resp = await self.app.get_client(self.lsp_serve_name()).send_lsg_msg(body)
                return resp

            def _call(msg):
                self.app.dispatch_lsp_msg(msg, serve_name)

            def _err(error):
                print('error :', error)

            try:
                method_name: str = method.__name__
                prefix, m = method_name.split('on', maxsplit=1)
                true_call = getattr(self, f'on_{m.lower()}')
                msg = true_call(*a, **kw)
                self.lsp_worker.add_coro(_send(msg), call_back=_call, err_back=_err)
            except:
                import traceback
                traceback.print_exc()
                raise

        return wrapper

    # region
    @send_to_language_serve
    def onInitialize(self):
        pass

    @send_to_language_serve
    def onTextDocumentFormatting(self):
        pass

    @send_to_language_serve
    def onTextDocumentDocumentHighlight(self):
        pass

    @send_to_language_serve
    def onTextDocumentDocumentSymbol(self):
        pass

    @send_to_language_serve
    def onTextDocumentFolding(self):
        pass

    @send_to_language_serve
    def onTextDocumentDocumentLink(self):
        pass

    @send_to_language_serve
    def onTextDocumentDidSave(self):
        pass

    @send_to_language_serve
    def onTextDocumentSignatureHelp(self):
        pass

    @send_to_language_serve
    def onTextDocumentDidChange(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentDidOpen(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentDidClose(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentInfer(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentCompletion(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentHover(self, word: str, line: int, col: int):
        pass

    @send_to_language_serve
    def onTextDocumentReferences(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentRename(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentSyntaxCheck(self, word: str, line, col):
        pass

    # endregion

    def on_initialize(self):
        with LspContext() as c:
            t = c.type
            params = t.InitializeParams(
                capabilities=self.clientCapacities(),
                client_info=self.client_info(),
                root_uri=self.app.lsp_root_uri(),
            )
            req = t.InitializeRequest(id=c.method_id.initialize_id, params=params)
            return c.body(req)

    def on_textdocumentreferences(self, word, line, col):
        with LspContext() as c:
            t = c.type
            # line, col = self.app.lsp_current_line_col()
            params = t.ReferenceParams(
                context=t.ReferenceContext(include_declaration=True),
                text_document=t.TextDocumentIdentifier(uri=self.app.lsp_current_document_uri()),
                position=t.Position(line=line, character=col)
            )
            r = t.TextDocumentReferencesRequest(id=c.method_id.textdocumentreferences_id, params=params)
            return c.body(r)

    def on_textdocumentformatting(self):
        raise NotImplementedError

    def on_textdocumentdocumenthighlight(self):
        raise NotImplementedError

    def on_textdocumentdocumentsymbol(self):
        raise NotImplementedError

    def on_textdocumentfolding(self):
        raise NotImplementedError

    def on_textdocumentdocumentlink(self):
        raise NotImplementedError

    def on_textdocumentdidsave(self):
        raise NotImplementedError

    def on_textdocumentsignaturehelp(self):
        raise NotImplementedError

    def on_textdocumentdidchange(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentdidopen(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentdidclose(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentinfer(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentcompletion_(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumenthover(self, word: str, line: int, col: int):
        raise NotImplementedError

    def on_textdocumentrename(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentsyntaxcheck(self, word: str, line, col):
        raise NotImplementedError
