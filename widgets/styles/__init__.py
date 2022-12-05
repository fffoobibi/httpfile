import warnings
import weakref
from contextlib import suppress
from typing import List, Type, Optional

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
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


def _run_trace_obj(change_theme=None):
    for obj, value in _styles_traces.items():
        QApplication.processEvents()
        try:
            func, a, kw = value
            func(obj, *a, change_theme, **kw)
        except:
            import traceback
            traceback.print_exc()


class BaseStyle(object):
    locked = False

    @classmethod
    def add_trace(cls, tag, func, *a, **kw):
        if tag not in _styles_traces.keys():
            _styles_traces[tag] = (func, a, kw)

    @classmethod
    def reload(cls):
        with suppress(Exception):
            del current_styles.__wrapped__
        # signal_manager.emit(signal_manager.themeChange)

    @classmethod
    def change(cls, theme_name: str):
        if theme_name not in _styles_clz.keys():
            warnings.warn('theme must in %s' % ','.join(_styles_clz.keys()))
            return
        if not cls.locked:
            cls.locked = True
            app = get_app_settings()
            app.setValue('theme', theme_name)
            cls.reload()
            _run_trace_obj(True)
            cls.locked = False

    @classmethod
    def theme_list(cls) -> List[str]:
        ret = []
        for k, v in _styles_clz.items():
            ret.append((k, v))

        ret.sort(key=lambda e: e[1]['index'])
        return list(map(lambda e: e[0], ret))

    @classmethod
    def get_editor_color(cls, style_colors: dict, style: int) -> Optional[str]:
        try:
            return style_colors.get(style)
        except:
            pass

    @classmethod
    def get_editor_font(cls, style_fonts: dict, style: int) -> Optional[QFont]:
        return style_fonts.get(style)

    menu: str = None
    tooltip: str = None
    tab: str = None  # tab
    run_tab: str = None  # run_tab
    splitter: str = None  # splitter qss

    menubar_background: str = None
    toolbar_background: str = None
    left_background: str = None

    border: str = None  # 边框色
    border_lighter: str = None

    background_darker: str = None
    background_lighter: str = None

    foreground: str = None
    hover: str = None

    handler: str = None
    progress: str = None

    guides_foreground: str = None  # 代码折叠线前台
    guides_background: str = None  # 代码折叠线前台

    bottom_button: dict = None  # 底部按钮
    left_button: dict = None  # 左侧按钮

    editor_globals: dict = None

    editor_json: dict = None
    editor_html: dict = None
    editor_python: dict = None
    editor_javascript: dict = None
    editor_http_file: dict = None
    editor_sql: dict = None
    editor_batch: dict = None
    editor_bash: dict = None
    editor_xml: dict = None
    editor_svg: dict = None
    editor_markdown: dict = None
    editor_common: dict = None
    editor_web_console: dict = None
    editor_run_console: dict = None

    def __init_subclass__(cls, **kwargs):
        super(BaseStyle, cls).__init_subclass__(**kwargs)
        editor_globals = cls.editor_globals
        for attr in [
            'editor_json',
            'editor_html',
            'editor_python',
            'editor_javascript',
            'editor_http_file',
            'editor_sql',
            'editor_batch',
            'editor_bash',
            'editor_xml',
            'editor_svg',
            'editor_markdown',
            'editor_common',
            'editor_web_console',
            'editor_run_console',
        ]:
            value = getattr(cls, attr)
            if editor_globals is not None:
                if value is None:
                    setattr(cls, attr, {})
                    value = getattr(cls, attr)
                for k, v in editor_globals.items():
                    self_value = value.get(k, None)
                    if self_value is not None:
                        dic = dict(**v)
                        dic.update(value[k])
                        value[k] = dic
                        # setattr(cls, attr, dic)
                        # print('set --', attr, dic)
                        # value[k].update(**v)
                    else:
                        value[k] = v
