# -*- coding: utf-8 -*-
# @Time    : 2022/12/9 10:57
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : interface.py
# @Software: PyCharm
import asyncio
import json
import re
from typing import Tuple


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

    async def send_lsg_msg(self, msg: dict) -> dict:
        content = json.dumps(msg, ensure_ascii=False).encode()
        header = f'Content-Length: {len(content)}\r\n'.encode()
        send_data = header + '\r\n'.encode() + content
        reader, writer = await self._get_reader_writer()
        writer.write(send_data)
        print('write msg: ', msg)
        await self.insure_write()
        return await self._recv_lsp_msg(reader)

    async def _recv_lsp_msg(self, reader: asyncio.StreamReader) -> dict:
        msg = b''
        headers_bytes = await reader.readuntil('\r\n\r\n'.encode())
        msg += headers_bytes
        headers = headers_bytes.decode()
        ret = re.findall(r'(?<=content-length:\s)(\d+)', headers, re.IGNORECASE)
        length = int(ret[0])
        line = await reader.read(length)
        content = line
        return json.loads(content.strip())

        # if line == b'':
        #     print('breadk -----')
        #     break
        # if line.decode() == '\r\n\r\n':
        #     break
        # print('get line: ', repr(line.decode()))
        # line = await reader.read()
        # msg += line
        # st = msg.decode()
        # print('recv msg---', st)
        # headers, content = st.split('\r\n\r\n')


class TCPLanguageClient(LanguageClientBase):

    async def insure_write(self):
        return await self._writer.drain()

    async def _get_reader_writer(self):
        if self._reader is None and self._writer is None and self._lock is False:
            self._lock = True
            host, port, loop = self.init_kw.get('host'), self.init_kw.get('port'), self.init_kw.get('loop')
            conn = asyncio.open_connection(host, port, loop=loop)
            reader, writer = await conn
            self._reader = reader
            self._writer = writer

        return self._reader, self._writer


class LSPAppMixIn(object):
    __lsp_serves__ = {}
    __lsp_clients__ = {}

    def create_lsp_serve(self, serve_name: str):
        pass

    def register_lsp_serve_params(self, info: tuple, factory):
        serve_name, init_kw = info
        self.__lsp_serves__.setdefault(serve_name, factory)

    def get_client(self, serve_name: str) -> LanguageClientBase:
        if self.__lsp_clients__.get(serve_name, None) is None:
            self.__lsp_clients__[serve_name] = self.__lsp_serves__.get(serve_name)()
        return self.__lsp_clients__[serve_name]

    def dispatch_lsp_msg(self, msg: dict, lsp_serve_name: str):
        raise NotImplementedError

    def lsp_initial(self, lsp_serve_name: str):
        raise NotImplementedError

    def lsp_root_uri(self):
        raise NotImplementedError

    def lsp_current_document_uri(self) -> str:
        raise NotImplementedError

    def lsp_current_line_col(self) -> Tuple[int]:
        raise NotImplementedError
