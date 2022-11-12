import typing as t

from functools import wraps

from pyqt5utils.components.styles import StylesHelper


def _styled_policy(t, policy):
    if policy == 'menu':
        StylesHelper.add_menu_style(t)
    elif policy == 'bottom_button':
        t.setStyleSheet('QPushButton{background: transparent; border:none; padding:3px 3px; font-family:微软雅黑}'
                        'QPushButton:hover{background: lightgray}')


def styled_factory(policy):
    def _after(clz, func_name):
        def decorator(func):
            @wraps(func)
            def inner(self, *a, **kw):
                getattr(clz, f'__old_force_{func_name}')(self, *a, **kw)
                ret = func(self, *a, **kw)
                return ret

            setattr(clz, f'__old_force_{func_name}', getattr(clz, func_name))
            return inner

        return decorator

    class StyledFactory(object):
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__()
            cls.__init__ = _after(cls, '__init__')(lambda this: _styled_policy(this, policy))

    return StyledFactory


T = t.TypeVar('T')


def make_styled(widget_clz: t.Type[T], policy, *a, **kw) -> T:
    obj = widget_clz(*a, **kw)
    _styled_policy(obj, policy)
    return obj
