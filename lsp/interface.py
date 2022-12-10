# -*- coding: utf-8 -*-
# @Time    : 2022/12/9 10:57
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : interface.py
# @Software: PyCharm
import asyncio
import json
import re
import subprocess
from typing import Tuple, IO, Optional

from attrs import asdict
from lsprotocol.types import ServerCapabilities
from lsprotocol.converters import get_converter

from widgets.hooks import register_lsp_hook


class LanguageClientBase(object):
    def __init__(self, serve_name: str, **init_kw):
        self.serve_name = serve_name
        self.init_kw = init_kw
        self._reader = None
        self._writer = None
        self._lock = False

    async def _get_reader_writer(self):
        raise NotImplementedError

    async def insure_write(self):
        raise NotImplementedError

    async def read_body(self, reader, length: int) -> bytes:
        raise NotImplementedError

    async def read_headers(self, reader) -> bytes:
        raise NotImplementedError

    async def send_lsg_msg(self, msg: dict) -> dict:
        content = json.dumps(msg, ensure_ascii=False).encode()
        header = f'Content-Length: {len(content)}\r\n'.encode()
        send_data = header + '\r\n'.encode() + content
        reader, writer = await self._get_reader_writer()
        # await asyncio.sleep(3)
        writer.write(send_data)
        await self.insure_write()
        return await self._recv_lsp_msg(reader)

    async def _recv_lsp_msg(self, reader) -> dict:
        msg = b''
        headers_bytes = await self.read_headers(reader)
        msg += headers_bytes
        headers = headers_bytes.decode()
        # print('headers: ', repr(headers))
        ret = re.findall(r'(?<=content-length:\s)(\d+)', headers, re.IGNORECASE)
        length = int(ret[0])
        line = await self.read_body(reader, length)
        content = line
        # print('body: ', content, len(content))
        return json.loads(content.decode().strip())


class StdIoLanguageClient(LanguageClientBase):

    async def read_body(self, reader, length):
        body = reader.read(length)
        return body

    async def read_headers(self, reader: IO[bytes]):
        msg = b''
        while True:
            line = reader.readline()
            msg += line
            if line == '\r\n'.encode():
                break

        return msg

    async def insure_write(self):
        self._writer.flush()

    async def _get_reader_writer(self):
        if self._reader is None and self._writer is None:
            reader, writer = self.init_kw.get('reader'), self.init_kw.get('writer')
            self._reader = reader
            self._writer = writer
        return self._reader, self._writer


class TCPLanguageClient(LanguageClientBase):

    async def read_body(self, reader: asyncio.StreamReader, length: int):
        # reader.readexactly()
        body = await reader.readexactly(length)

        return body

    async def read_headers(self, reader: asyncio.StreamReader):
        msg = b''
        while True:
            line = await reader.readline()
            msg += line
            if line == '\r\n'.encode():
                break
        return msg
        # ret = await reader.readuntil('\r\n\r\n'.encode())
        # return ret

    async def insure_write(self):
        await self._writer.drain()

    async def _get_reader_writer(self):
        if self._reader is None and self._writer is None:
            host, port, loop = self.init_kw.get('host'), self.init_kw.get('port'), self.init_kw.get('loop')
            conn = asyncio.open_connection(host, port, loop=loop)
            reader, writer = await conn
            self._reader = reader
            self._writer = writer

        return self._reader, self._writer


class LSPAppMixIn(object):
    __lsp_serves__ = {}
    __lsp_clients__ = {}
    __lsp_serve_capacities__ = {}

    def create_lsp_hook_func(self, serve_name: str, cap: ServerCapabilities, editor):
        from lsp.lsp_interface import LanguageServerMixIn
        editor: LanguageServerMixIn
        print('run hooks---- ', serve_name, cap)
        for k in ['hover_provider',
                  'document_symbol_provider',
                  'references_provider',
                  'rename_provider',
                  'completion_provider',
                  'diagnostic_provider', ]:
            field = getattr(cap, k, None)
            flag = getattr(editor, editor.lsp_maps[k])
            if isinstance(field, (bool, None.__class__)):
                if field:
                    editor.support_enabled(flag)
                else:
                    editor.support_enabled(flag)
            else:
                editor.support_enabled(flag)

    def register_lsp_serve_capacities(self, serve_name: str, cap_dict: dict) -> ServerCapabilities:
        from widgets.signals import signal_manager
        server_cap = get_converter().structure(cap_dict, ServerCapabilities)
        self.__lsp_serve_capacities__.setdefault(serve_name, server_cap)
        # self.settings.beginGroup(f'{serve_name}')
        # for k in ['hover_provider',
        #           'document_symbol_provider',
        #           'references_provider',
        #           'rename_provider',
        #           'completion_provider',
        #           'diagnostic_provider', ]:
        #     field = getattr(server_cap, k, None)
        #     if isinstance(field, (bool, None.__class__)):
        #         self.settings.setValue(k, field)
        #     else:
        #         self.settings.setValue(k, asdict(field))
        # self.settings.endGroup()
        print('regis hook ', serve_name)
        register_lsp_hook(serve_name, lambda s, editor: self.create_lsp_hook_func(s, server_cap, editor))
        signal_manager.emit(signal_manager.runLspHook, serve_name)
        return server_cap

    def get_lsp_capacities(self, lsp_name: str) -> Optional[ServerCapabilities]:
        return self.__lsp_serve_capacities__.get(lsp_name)

    def register_lsp_serve_params(self, info: tuple, factory, flag: str):
        if flag == 'tcp':
            serve_name, init_kw = info
            self.__lsp_serves__.setdefault(serve_name, factory)
        elif flag == 'stdio':
            serve_name, init_kw = info
            self.__lsp_serves__.setdefault(serve_name, factory)

    def get_client(self, serve_name: str) -> LanguageClientBase:
        if self.__lsp_clients__.get(serve_name, None) is None:
            if isinstance(self.__lsp_serves__[serve_name], subprocess.Popen):
                self.__lsp_clients__[serve_name] = self.__lsp_serves__.get(serve_name)()
            else:
                self.__lsp_clients__[serve_name] = self.__lsp_serves__.get(serve_name)()
        return self.__lsp_clients__[serve_name]

    def dispatch_lsp_msg(self, msg: dict, lsp_serve_name: str, file_path: str):
        raise NotImplementedError

    def lsp_initial(self, lsp_serve_name: str):
        raise NotImplementedError

    def lsp_root_uri(self):
        raise NotImplementedError

    def lsp_current_document_uri(self) -> str:
        raise NotImplementedError

    def lsp_current_line_col(self) -> Tuple[int]:
        raise NotImplementedError
