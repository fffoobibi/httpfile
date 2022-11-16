import warnings
import weakref

from contextlib import suppress
from typing import List, Type

from lazy_object_proxy import Proxy

from widgets.base import get_app_settings
from widgets.signals import signal_manager

module_name = 'widgets.styles'

_styles_clz = {}

_styles_traces = weakref.WeakKeyDictionary()

__all__ = ('load_style_clz', 'current_styles')


def _current_styles():
    app = get_app_settings()
    style_clz_name = app.value('theme', defaultValue='dark')
    return _styles_clz.get(style_clz_name, {}).get('clz')


current_styles: Type['BaseStyle'] = Proxy(_current_styles)


def register(name: str, index: int = 0, icon: str = None):
    def wrapper(clz):
        _styles_clz.setdefault(name, dict(icon=icon, index=index, clz=clz))
        return clz

    return wrapper


def load_style_clz():
    from pathlib import Path
    from importlib import import_module
    dir_path = Path(__file__).parent
    for path_ in dir_path.iterdir():
        if path_.name.startswith('style_'):
            file, _ = path_.name.split('.')
            import_module(f'.{file}', module_name)
    return _styles_clz


def _run_trace_obj():
    for obj, value in _styles_traces.items():
        with suppress(Exception):
            func, a, kw = value
            func(obj, *a, **kw)


class BaseStyle(object):

    @classmethod
    def add_trace(cls, tag, func, *a, **kw):
        if tag not in _styles_traces.keys():
            _styles_traces[tag] = (func, a, kw)

    @classmethod
    def reload(cls):
        with suppress(Exception):
            del current_styles.__wrapped__
        signal_manager.emit(signal_manager.themeChange)

    @classmethod
    def change(cls, theme_name: str):
        if theme_name not in _styles_clz.keys():
            warnings.warn('theme must in %s' % ','.join(_styles_clz.keys()))
            return
        app = get_app_settings()
        app.setValue('theme', theme_name)
        _run_trace_obj()
        cls.reload()

    @classmethod
    def theme_list(cls) -> List[str]:
        ret = []
        for k, v in _styles_clz.items():
            ret.append((k, v))

        ret.sort(key=lambda e: e[1]['index'])
        return list(map(lambda e: e[0], ret))

    menu = ''
