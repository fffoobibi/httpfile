# -*- coding: utf-8 -*-
# @Time    : 2022/12/11 8:09
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : loggers.py
# @Software: PyCharm
import logging
from typing import Union
from typing_extensions import Literal

__all__ = (
    'lsp_logger', 'console_logger', 'with_trace_back'
)

lsp_logger: logging.Logger = None
console_logger: logging.Logger = None


def create_logger():
    global lsp_logger, console_logger
    if lsp_logger is None:
        basic_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s %(filename)s, line %(lineno)d: %(message)s')

        lsp_logger = logging.getLogger('lsp-logger')
        lsp_logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(basic_formatter)
        lsp_logger.addHandler(handler)

        console_logger = logging.getLogger('console')
        console_logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(basic_formatter)
        console_logger.addHandler(handler)


create_logger()


# decorate
def with_trace_back(logger: Union[Literal['lsp', 'console'], logging.Logger], display: bool = True):
    def wrapper(func):
        if isinstance(logger, str):
            if logger == 'lsp':
                l = lsp_logger
            elif logger == 'console':
                l = console_logger
            else:
                l = logging.getLogger()
        else:
            l = logger

        def inner(*a, **kw):
            try:
                return func(*a, **kw)
            except Exception:
                if display:
                    l.error('error trace back', exc_info=True)
                else:
                    l.debug('error debug', exc_info=True)

        return inner

    return wrapper
