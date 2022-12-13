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
from widgets.loggers import lsp_logger

_lsp_context = LspContext()
_t = _lsp_context.type
_method_id = _lsp_context.method_id


class ILanguageServe(object):
    def capacities(self) -> int:
        return 0

    @classmethod
    def lsp_serve_name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def lsp_init_kw(cls) -> dict:
        raise NotImplementedError

    @classmethod
    def clientCapacities(cls) -> ClientCapabilities:
        raise NotImplementedError


class ILanguageServeImp(object):
    @classmethod
    def on_initialize(cls, client_cap: _t.ClientCapabilities, client_info: _t.InitializeParamsClientInfoType = None,
                      root_uri: str = None, ):
        raise NotImplementedError

    @classmethod
    def on_textdocumentdiagnosticrequest(cls, file_path: str):
        raise NotImplementedError

    @classmethod
    def on_textdocumentformatting(cls, file_path: str):
        raise NotImplementedError

    @classmethod
    def on_textdocumentdocumenthighlight(cls, file_path: str):
        raise NotImplementedError

    @classmethod
    def on_textdocumentdocumentsymbol(cls, file_path: str):
        raise NotImplementedError

    @classmethod
    def on_textdocumentfolding(cls):
        raise NotImplementedError

    @classmethod
    def on_textdocumentdocumentlink(cls):
        raise NotImplementedError

    @classmethod
    def on_textdocumentdidsave(cls, file_path: str):
        raise NotImplementedError

    @classmethod
    def on_textdocumentsignaturehelp(cls):
        raise NotImplementedError

    @classmethod
    def on_textdocumentdidchange(cls, file_path: str, text: str, version: int):
        raise NotImplementedError

    @classmethod
    def on_textdocumentdidopen(cls, file_path: str, language_id: str,
                               version: int, text: str):
        raise NotImplementedError

    @classmethod
    def on_textdocumentdidclose(cls, file_path: str):
        raise NotImplementedError

    @classmethod
    def on_textdocumentinfer(cls, word: str, line, col):
        raise NotImplementedError

    @classmethod
    def on_textdocumentcompletion(cls, word: str, line, col):
        raise NotImplementedError

    @classmethod
    def on_textdocumenthover(cls, word: str, line: int, col: int,
                             file_path: str):
        raise NotImplementedError

    @classmethod
    def on_textdocumentreferences(cls, word: str, line: int, col: int):
        raise NotImplementedError

    @classmethod
    def on_textdocumentrename(cls, word: str, line, col):
        raise NotImplementedError

    @classmethod
    def on_textdocumentpublishdiagnostics(cls, file_path: str, version: int,
                                          start_line: int, start_col: int,
                                          end_line: int, end_col: int):
        raise NotImplementedError

    @classmethod
    def on_textdocumentcolor(cls, file_path: str):
        pass


class LanguageServerMixIn(ILanguageServe, ILanguageServeImp):
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

    app: LSPAppMixIn  # type hint,  flag

    def capacities(self) -> int:
        return 0

    @cached_property
    def lsp_worker(self):
        return WorkerManager().get('lsp-worker')

    @classmethod
    def _client(cls):
        serve_name, init_kw = cls.client_init_params()
        return cls.language_client_class(serve_name, **init_kw)

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
            if inspect.isfunction(v) and (
                    v.__name__.startswith('on_') or v.__name__ in ['capacities',
                                                                   'lsp_init_kw',
                                                                   'clientCapacities',
                                                                   'lsp_serve_name']):
                bound_method = types.MethodType(v, self)
                setattr(self, k, bound_method)

    #### language server protocol ###

    @classmethod
    def client_init_params(cls) -> Tuple:
        lsp_name = None
        try:
            lsp_name = cls.lsp_serve_name()
            start_lsp = cls.lsp_init_kw()
            return lsp_name, start_lsp
        except:
            name = lsp_name or '[default]'
            lsp_logger.warning(f'{name} start fail', exc_info=True)

    @classmethod
    def register_to_app(cls, main_app: LSPAppMixIn) -> bool:
        if getattr(cls, 'app', None) is None:
            cls.app = main_app
            if cls.language_client_class is TCPLanguageClient:
                return main_app.register_lsp_serve_params(cls.client_init_params(),
                                                          cls._client, 'tcp')
            elif cls.language_client_class is StdIoLanguageClient:
                return main_app.register_lsp_serve_params(cls.client_init_params(),
                                                          cls._client, 'stdio')
        return True

    @classmethod
    def client_info(cls) -> InitializeParamsClientInfoType:
        return InitializeParamsClientInfoType(
            name='fxk-editor',
            version='1.0.0'
        )

    # decorator
    def send_to_language_serve_in_thread(method):
        def wrapper(self, *a, **kw):
            serve_name = self.lsp_serve_name()
            worker = WorkerManager().get('lsp-worker')

            async def _send(body):
                try:
                    try:
                        path = self.app.current_file_path()
                    except:
                        path = None
                    if isinstance(body, tuple):
                        body, method_name_ = body
                    lsp_logger.info(f'{self} request {body.get("method")}')
                    client = self.app.get_client(serve_name)
                    resp = await client.send_lsg_msg(body)
                    return resp, path
                except:
                    raise

            def _call(msg_path):
                msg_, path = msg_path
                self.app.dispatch_lsp_msg(msg_, serve_name, path)

            def _err(error):
                pass

            try:
                method_name: str = method.__name__
                prefix, m = method_name.split('on', maxsplit=1)
                true_call = getattr(self, f'on_{m.lower()}')
                msg = true_call(*a, **kw)
                worker.add_coro(_send(msg), call_back=_call,
                                err_back=_err)
            except:
                raise

        return wrapper

    # region
    @classmethod
    @send_to_language_serve_in_thread
    def onInitialize(cls, client_cap: _t.ClientCapabilities, client_info: _t.InitializeParamsClientInfoType = None,
                     root_uri: str = None):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentDiagnosticRequest(cls, file_path: str):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentFormatting(cls, file_path: str):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentDocumentHighlight(cls, file_path: str):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentDocumentSymbol(cls, file_path: str):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentFolding(cls):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentDocumentLink(cls):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentDidSave(cls):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentSignatureHelp(cls):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentInfer(cls, word: str, line, col):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentCompletion(cls, word: str, line, col, file_path: str):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentHover(cls, word: str, line: int, col: int,
                            file_path: str):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentReferences(cls, word: str, line, col):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentRename(cls, word: str, line, col):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentColor(cls, file_path: str):
        pass

    # notifations
    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentDidOpen(cls, file_path: str, language_id: str,
                              version: int, text: str):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentDidChange(cls, file_path: str, text: str, version: int):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentDidClose(cls, file_path: str):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentDidSave(cls, file_path: str):
        pass

    @classmethod
    @send_to_language_serve_in_thread
    def onTextDocumentPublishDiagnostics(cls, file_path: str, version: int,
                                         start_line: int, start_col: int,
                                         end_line: int, end_col: int):
        pass

    # endregion

    # notifications
    @classmethod
    def on_textdocumentpublishdiagnostics(cls, file_path: str, version: int,
                                          start_line: int, start_col: int,
                                          end_line: int, end_col: int
                                          ):
        params = _t.PublishDiagnosticsParams(
            uri=f'file:///{file_path}',
            diagnostics=[_t.Diagnostic(
                range=_t.Range(
                    start=_t.Position(line=start_line, character=start_col),
                    end=_t.Position(line=end_line, character=end_col)
                ),
                message='test'
            )],
        )
        r = _t.TextDocumentPublishDiagnosticsNotification(
            params=params
        )
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumentdidopen(cls, file_path: str, language_id: str,
                               version: int, text: str):
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

    @classmethod
    def on_textdocumentdidchange(cls, file_path: str, text: str, version: int):
        params = _t.DidChangeTextDocumentParams(
            text_document=_t.VersionedTextDocumentIdentifier(
                version=version,
                uri=f'file:///{file_path}'),
            content_changes=[_t.TextDocumentContentChangeEvent_Type2(text=text)]
            # full
        )
        r = _t.TextDocumentDidChangeNotification(
            params=params
        )
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumentdidsave(cls, file_path: str):
        params = _t.DidSaveTextDocumentParams(
            text_document=_t.VersionedTextDocumentIdentifier(
                uri=f'file:///{file_path}'),
        )
        r = _t.TextDocumentDidSaveNotification(
            params=params
        )
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumentdidclose(cls, file_path: str):
        params = _t.DidCloseTextDocumentParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}')
        )
        r = _t.TextDocumentDidCloseNotification(
            params=params
        )
        return _lsp_context.body(r)

    # normal
    @classmethod
    def on_initialize(cls, client_cap: _t.ClientCapabilities, client_info: _t.InitializeParamsClientInfoType = None,
                      root_uri: str = None,
                      ):
        with LspContext() as c:
            t = c.type
            params = t.InitializeParams(
                capabilities=client_cap,  # self.clientCapacities(),
                client_info=client_info,  # self.client_info(),
                root_uri=root_uri,  # self.app.lsp_root_uri(),

                work_done_token=c.token.initialize_token
            )
            req = t.InitializeRequest(id=c.method_id.initialize_id,
                                      params=params)
            return c.body(req, method_name=t.INITIALIZE)

    @classmethod
    def on_textdocumentdiagnosticrequest(cls, file_path: str):
        params = _t.DocumentDiagnosticParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}'),
            work_done_token=_lsp_context.token.diagnosticrequest_token
        )
        r = _t.TextDocumentDiagnosticRequest(
            id=_method_id.textdocumentdiagnosticrequest_id,
            params=params
        )
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumentreferences(cls, word, line, col):
        params = _t.ReferenceParams(
            context=_t.ReferenceContext(include_declaration=True),
            text_document=_t.TextDocumentIdentifier(
                uri=cls.app.lsp_current_document_uri()),
            position=_t.Position(line=line, character=col)
        )
        r = _t.TextDocumentReferencesRequest(
            id=c.method_id.textdocumentreferences_id, params=params)
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumentdocumenthighlight(cls, file_path: str):
        params = _t.DocumentHighlightParams(
            text_document=_t.TextDocumentIdentifier(
                uri=f'file:///{file_path}'),
            position=_t.Position(line=8, character=43)
        )
        r = _t.TextDocumentDocumentHighlightRequest(
            id=_method_id.method_id.textdocumentdocumenthighlight_id,
            params=params
        )
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumentdocumentsymbol(cls, file_path: str):
        params = _t.DocumentSymbolParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}')
        )
        r = _t.TextDocumentDocumentSymbolRequest(
            id=_method_id.textdocumentdocumentsymbol_id,
            params=params
        )
        resp = _t.TextDocumentDocumentSymbolResponse
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumentcolor(cls, file_path: str):
        params = _t.DocumentColorParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}')
        )
        r = _t.TextDocumentDocumentColorRequest(
            id=_method_id.textdocumentcolor_id,
            params=params
        )
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumentformatting(cls, file_path: str):
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

    @classmethod
    def on_textdocumentfolding(cls):
        raise NotImplementedError

    @classmethod
    def on_textdocumentdocumentlink(cls):
        raise NotImplementedError

    @classmethod
    def on_textdocumentsignaturehelp(cls):
        raise NotImplementedError

    @classmethod
    def on_textdocumentinfer(cls, word: str, line, col):
        raise NotImplementedError

    @classmethod
    def on_textdocumentcompletion(cls, word: str, line, col, file_path):
        params = _t.CompletionParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}'),
            position=_t.Position(line=line, character=col - 1)
        )
        r = _t.TextDocumentCompletionRequest(
            id=_method_id.textdocumentcompletion_id,
            params=params
        )
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumenthover(cls, word: str, line: int, col: int,
                             file_path: str):
        params = _t.HoverParams(
            text_document=_t.TextDocumentIdentifier(uri=f'file:///{file_path}'),
            position=_t.Position(line=line, character=col - 1)
        )
        r = _t.TextDocumentHoverRequest(
            id=_method_id.textdocumenthover_id,
            params=params
        )
        return _lsp_context.body(r)

    @classmethod
    def on_textdocumentrename(cls, word: str, line, col):
        raise NotImplementedError
