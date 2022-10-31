# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 9:48
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : http.py
# @Software: PyCharm

import asyncio
import aiohttp

from typing import Callable, Dict, List, Type
from types import MethodType
from enum import Enum
from pyqt5utils.decorators import singleton
from pyqt5utils._types import SingletonType
from pyqt5utils.managers import DomainManager, Domains, LoggerManager


try:
    from typing_extensions import Literal
except ImportError:
    from typing import Literal

from pyqt5utils.workers import BackgroundWorker


__all__ = (
    'Http', 'ApiPath'
)


class RequestProxy(object):
    _request_worker = BackgroundWorker()
    _timeout_obj = object()

    def copy(self):
        ret = self.__class__(self.decorate_func, self.path, self._domain, self._qt_obj, self.prefix, self.data,
                             self.params,
                             self.headers, self.logger, self._time_out, self.ret)
        ret._instance = self._instance
        ret._before = self._before
        ret._success = self._success
        ret._fail = self._fail
        ret._both = self._both
        ret._if = self._if
        return ret

    def __init__(self, decorate_func: Callable, path: "ApiPath", domain: str, qt_obj: str = None, prefix='post',
                 data=None, params=None,
                 headers=None, logger=None, time_out=60,
                 ret: Literal['json', 'text'] = 'json', ):
        self.decorate_func = decorate_func
        self.path = path
        self.prefix = prefix
        self.data = data
        self.params = params
        self.headers = headers
        self.logger = logger
        self.ret = ret
        self._domain = domain
        self._time_out = time_out
        self._qt_obj = qt_obj
        self._instance = None
        self._before = None
        self._success = None
        self._fail = None
        self._both = None
        self._if = None

    def __get__(self, ins, owner=None):
        self._instance = ins
        return self

    def __call__(self, *args, **kwargs):
        return self.decorate_func(self._instance, *args, **kwargs)

    def if_(self, func):
        self._if = func
        return self

    def success(self, func):
        self._success = func
        return func

    def fail(self, func):
        self._fail = func
        return func

    def before(self, func):
        self._before = func
        return func

    def both(self, func):
        self._both = func
        return func

    def get(self):
        pass

    def _get(self):
        pass

    def post(self, *a, **kw):
        if self._qt_obj:
            try:
                getattr(self._instance, self._qt_obj).setEnabled(False)
            except:
                import traceback
                traceback.print_exc()

        if self._before:
            self._before(self._instance)

        ret = self.decorate_func(self._instance)

        d = self.data or {}
        p = self.params or {}
        h = self.headers or {}

        if isinstance(self.data, aiohttp.FormData):
            d = self.data
        elif isinstance(self.data, dict):
            d.update(ret.get('data', {}))
            d.update(**kw.pop('data', {}))
        else:
            d = None

        if isinstance(self.params, dict):
            p.update(ret.get('params', {}))
            p.update(**kw.pop('params', {}))
        else:
            p = {}

        if isinstance(self.headers, dict):
            h.update(ret.get('headers', {}))
            h.update(**kw.pop('headers', {}))
        else:
            h = {}

        coro = self._post(d, h, p, self._time_out)
        self._request_worker.add_coro(
            coro, call_back=self._call_back, err_back=self._err_back)
        return ResponseProxy(self)

    async def _post(self, d, h, p, time_out):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=time_out)) as session:
            url = self._domain + self.path
            await asyncio.sleep(2)
            try:
                async with session.post(url, headers=h, data=d,
                                        params=p) as resp:
                    resp.raise_for_status()
                    if self.ret == 'json':
                        try:
                            return await resp.json()
                        except:
                            return await resp.json(content_type=None)
                    else:
                        text = await resp.text()
                        return text
            except asyncio.TimeoutError:
                return self._timeout_obj

    def _call_back(self, ret):
        if ret == self._timeout_obj:
            if self._time_out:
                self._time_out()
        else:
            if self._success:
                self._success(self._instance, ret)
            if self._both:
                self._both(self._instance)
            if self._qt_obj:
                try:
                    getattr(self._instance, self._qt_obj).setEnabled(True)
                except:
                    pass

    def _err_back(self, error):
        if self.logger:
            self.logger.error(error, exc_info=True)
        if self._fail:
            self._fail(self._instance, error)
        if self._both:
            self._both(self._instance)
        if self._qt_obj:
            try:
                getattr(self._instance, self._qt_obj).setEnabled(True)
            except:
                pass

    def __add__(self, other: "RequestProxy"):
        if not isinstance(other, RequestProxy):
            raise TypeError('must be `RequestProxy`')

        def _call_back(this, ret):
            self._call_back(ret)
            value = {}
            if other._if is not None:
                try:
                    flag, value = other._if(ret)
                except:
                    flag = False
            else:
                flag = True
            if flag:
                other.post(**value)

        out_put = self.copy()
        out_put._call_back = MethodType(_call_back, out_put)
        return out_put

    def __str__(self) -> str:
        return f'RequestProxy<{self.path}>'


class ResponseProxy(object):

    def __init__(self, request: RequestProxy) -> None:
        self.request = request

    def data(self):
        pass

    def fetch(self, *a, **kw):
        pass


class ApiPath(str, Enum):
    pass


class Http(object):
    dm = DomainManager
    lm = LoggerManager
    assert issubclass(dm, SingletonType)
    assert issubclass(lm, SingletonType)

    config = dict(
        time_out=60,
        headers={},
        params={}
    )

    @classmethod
    def add_request_handle(cls, request):
        return request

    @classmethod
    def add_response_handle(cls, response):
        return response

    @classmethod
    def add_error_handle(cls, error):
        return error

    @classmethod
    def add_timeout_handle(cls, request):
        return

    @classmethod
    def decorate_post(cls, path: ApiPath, domain_type: str, data=None, params=None, headers=None, ret: Literal['text', 'json'] = 'text',
                      time_out=None, logger_name: str = None,
                      qt_obj: str = None, ):
        def wrapper(func):
            t = cls.config.get('time_out', None)
            _t = time_out if time_out is not None else (t or 60)
            return RequestProxy(func, path, cls.dm().get_domain(domain_type), qt_obj, data, params, headers, ret=ret,
                                time_out=_t, logger=cls.lm().get_logger(logger_name))

        return wrapper

    @classmethod
    def decorate_get(cls):
        pass

    def post(self, path: ApiPath, field_type: str, data=None, params=None, headers=None, time_out=None):
        assert isinstance(
            self, SingletonType), 'use @singleton to decorate your custom class !'

    def get(self, path: ApiPath, field_type: str, params=None, headers=None, time_out=None):
        assert isinstance(
            self, SingletonType), 'use @singleton to decorate your custom class !'
