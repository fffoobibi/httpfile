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

from lsp.interface import LSPAppMixIn, TCPLanguageClient, StdIoLanguageClient
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

    def on_textdocumentformatting(self, file_path: str):
        raise NotImplementedError

    def on_textdocumentdocumenthighlight(self, file_path: str):
        raise NotImplementedError

    def on_textdocumentdocumentsymbol(self, file_path: str):
        raise NotImplementedError

    def on_textdocumentfolding(self):
        raise NotImplementedError

    def on_textdocumentdocumentlink(self):
        raise NotImplementedError

    def on_textdocumentdidsave(self, file_path: str):
        raise NotImplementedError

    def on_textdocumentsignaturehelp(self):
        raise NotImplementedError

    def on_textdocumentdidchange(self, file_path: str, text: str, version: int):
        raise NotImplementedError

    def on_textdocumentdidopen(self, file_path: str, language_id: str, version: int, text: str):
        raise NotImplementedError

    def on_textdocumentdidclose(self, file_path: str):
        raise NotImplementedError

    def on_textdocumentinfer(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentcompletion(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumenthover(self, word: str, line: int, col: int, file_path: str):
        raise NotImplementedError

    def on_textdocumentreferences(self, word: str, line: int, col: int):
        raise NotImplementedError

    def on_textdocumentrename(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentpublishdiagnostics(self, file_path: str, version: int):
        raise NotImplementedError

    def on_textdocumentcolor(self, file_path: str):
        pass


_lsp_context = LspContext()
_t = _lsp_context.type
_method_id = _lsp_context.method_id


class LanguageServerMixIn(ILanguageServe):
    language_client_class: 'TCPLanguageClient'

    language_mask = 0
    rename_flag = 1
    infer_flag = 1 << 1
    completion_flag = 1 << 2
    hover_flag = 1 << 3
    ref_flag = 1 << 4
    syntax_flag = 1 << 5
    symbol_flag = 1 << 6
    format_flag = 1 << 7

    lsp_maps = {
        'hover_provider': 'hover_flag',
        'document_symbol_provider': 'symbol_flag',
        'references_provider': 'ref_flag',
        'rename_provider': 'rename_flag',
        'completion_provider': 'completion_flag',
        'diagnostic_provider': 'syntax_flag',
        'document_formatting_provider': 'format_flag'
    }

    app: LSPAppMixIn  # type hint

    @cached_property
    def lsp_worker(self):
        return WorkerManager().get('lsp-worker')

    def _client(self):
        serve_name, init_kw = self.client_init_params()
        return self.language_client_class(serve_name, **init_kw)

    def support_enabled(self, flags: int):
        self.language_mask |= flags

    def supported(self, flag: int) -> bool:
        return self.language_mask & flag

    def support_disabled(self, flag: int):
        # if self.supported(flag):
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

    ## hook
    def run_hook(self):
        pass

    def client_init_params(self) -> Tuple:
        params = self.lsp_serve_name(), self.lsp_init_kw()
        return params

    def register_to_app(self, main_app: LSPAppMixIn):
        self.app = main_app
        if self.language_client_class is TCPLanguageClient:
            main_app.register_lsp_serve_params(self.client_init_params(), self._client, 'tcp')
        elif self.language_client_class is StdIoLanguageClient:
            main_app.register_lsp_serve_params(self.client_init_params(), self._client, 'stdio')

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
            path = self.file_path()

            async def _send(body):
                try:
                    if isinstance(body, tuple):
                        body, method_name = body
                    client = self.app.get_client(serve_name)
                    resp = await client.send_lsg_msg(body)
                    return resp
                except:
                    import traceback
                    traceback.print_exc()
                    raise

            def _call(msg):
                self.app.dispatch_lsp_msg(msg, serve_name, path)
                # if method.__name__ == 'onInitialize':
                #     server_cap = _lsp_context.converter.structure(msg['result']['capabilities'],
                #                                                   _lsp_context.type.ServerCapabilities)

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
    def onTextDocumentFormatting(self, file_path: str):
        pass

    @send_to_language_serve
    def onTextDocumentDocumentHighlight(self, file_path: str):
        pass

    @send_to_language_serve
    def onTextDocumentDocumentSymbol(self, file_path: str):
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
    def onTextDocumentInfer(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentCompletion(self, word: str, line, col, file_path: str):
        pass

    @send_to_language_serve
    def onTextDocumentHover(self, word: str, line: int, col: int, file_path: str):
        pass

    @send_to_language_serve
    def onTextDocumentReferences(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentRename(self, word: str, line, col):
        pass

    @send_to_language_serve
    def onTextDocumentColor(self, file_path: str):
        pass

    # notifations
    @send_to_language_serve
    def onTextDocumentDidOpen(self, file_path: str, language_id: str, version: int, text: str):
        pass

    @send_to_language_serve
    def onTextDocumentDidChange(self, file_path: str, text: str):
        pass

    @send_to_language_serve
    def onTextDocumentDidClose(self, file_path: str):
        pass

    @send_to_language_serve
    def onTextDocumentDidSave(self, file_path: str):
        pass

    @send_to_language_serve
    def onTextDocumentPublishDiagnostics(self, file_path: str, version: int):
        pass

    # endregion

    # notifications
    def on_textdocumentpublishdiagnostics(self, file_path: str, version: int):
        params = _t.PublishDiagnosticsParams(
            uri=f'file:///{file_path}',
            diagnostics=_t.Diagnostic(),
            # version=version,
        )
        r = _t.TextDocumentPublishDiagnosticsNotification(
            params=params
        )
        _t.TextDocumentDiagnosticResponse
        return _lsp_context.body(r)

    def on_textdocumentdidopen(self, file_path: str, language_id: str, version: int, text: str):
        params = _t.DidOpenTextDocumentParams(
            text_document=_t.TextDocumentItem(uri=f'file:///{file_path}',
                                              language_id=language_id,
                                              version=version,
                                              text=text,
                                              ))
        r = _t.TextDocumentDidOpenNotification(
            params=params
        )
        return _lsp_context.body(r)

    def on_textdocumentdidchange(self, file_path: str, text: str, version: int):
        params = _t.DidChangeTextDocumentParams(
            text_document=_t.VersionedTextDocumentIdentifier(
                version=version,
                uri=f'file:///{file_path}'),
            content_changes=_t.TextDocumentContentChangeEvent_Type2(text=text)  # full
        )
        r = _t.TextDocumentDidChangeNotification(
            params=params
        )
        return _lsp_context.body(r)

    def on_textdocumentdidsave(self, file_path: str):
        params = _t.DidSaveTextDocumentParams(
            text_document=_t.VersionedTextDocumentIdentifier(
                uri=f'file:///{file_path}'),
        )
        r = _t.TextDocumentDidSaveNotification(
            params=params
        )
        return _lsp_context.body(r)

    def on_textdocumentdidclose(self, file_path: str):
        params = _t.DidCloseTextDocumentParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}')
        )
        r = _t.TextDocumentDidCloseNotification(
            params=params
        )
        return _lsp_context.body(r)

    # normal

    def on_initialize(self):
        with LspContext() as c:
            t = c.type
            params = t.InitializeParams(
                capabilities=self.clientCapacities(),
                client_info=self.client_info(),
                root_uri=self.app.lsp_root_uri(),
                work_done_token=c.token.initialize_token
            )
            req = t.InitializeRequest(id=c.method_id.initialize_id, params=params)
            return c.body(req, method_name=t.INITIALIZE)

    def on_textdocumentreferences(self, word, line, col):
        # if self.app.get_lsp_capacities(self.lsp_serve_name())
        with LspContext() as c:
            t = c.type
            params = t.ReferenceParams(
                context=t.ReferenceContext(include_declaration=True),
                text_document=t.TextDocumentIdentifier(uri=self.app.lsp_current_document_uri()),
                position=t.Position(line=line, character=col)
            )
            r = t.TextDocumentReferencesRequest(id=c.method_id.textdocumentreferences_id, params=params)
            return c.body(r)

    def on_textdocumentdocumenthighlight(self, file_path: str):
        with LspContext() as c:
            t = c.type
            params = t.DocumentHighlightParams(
                text_document=t.TextDocumentIdentifier(uri=f'file:///{file_path}'),
                position=t.Position(line=8, character=43)
            )
            r = t.TextDocumentDocumentHighlightRequest(
                id=c.method_id.textdocumentdocumenthighlight_id,
                params=params
            )
            return c.body(r)

    def on_textdocumentdocumentsymbol(self, file_path: str):
        params = _t.DocumentSymbolParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}')
        )
        r = _t.TextDocumentDocumentSymbolRequest(
            id=_method_id.textdocumentdocumentsymbol_id,
            params=params
        )
        return _lsp_context.body(r)

    def on_textdocumentcolor(self, file_path: str):
        params = _t.DocumentColorParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}')
        )
        r = _t.TextDocumentDocumentColorRequest(
            id=_method_id.textdocumentcolor_id,
            params=params
        )
        return _lsp_context.body(r)

    def on_textdocumentformatting(self, file_path: str):
        params = _t.DocumentFormattingParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}'),
            options=_t.FormattingOptions(
                tab_size=4,
                insert_spaces=True,
                trim_trailing_whitespace=True
            ),
            work_done_token=_lsp_context.token.formatting_token
        )
        r = _t.TextDocumentFormattingRequest(
            id=_method_id.textdocumentformatting_id,
            params=params
        )
        return _lsp_context.body(r)

    def on_textdocumentfolding(self):
        raise NotImplementedError

    def on_textdocumentdocumentlink(self):
        raise NotImplementedError

    def on_textdocumentsignaturehelp(self):
        raise NotImplementedError

    def on_textdocumentinfer(self, word: str, line, col):
        raise NotImplementedError

    def on_textdocumentcompletion(self, word: str, line, col, file_path):
        params = _t.CompletionParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}'),
            position=_t.Position(line=line, character=col - 1)
        )
        r = _t.TextDocumentCompletionRequest(
            id=_method_id.textdocumentcompletion_id,
            params=params
        )
        return _lsp_context.body(r)

    def on_textdocumenthover(self, word: str, line: int, col: int, file_path: str):
        params = _t.HoverParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}'),
            position=_t.Position(line=line, character=col - 1)
        )
        r = _t.TextDocumentHoverRequest(
            id=_method_id.textdocumenthover_id,
            params=params
        )
        return _lsp_context.body(r)

    def on_textdocumentrename(self, word: str, line, col):
        raise NotImplementedError
