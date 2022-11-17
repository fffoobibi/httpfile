import typing as t
from functools import wraps

from widgets.styles import current_styles


def _styled_policy(t, policy):
    if policy == 'menu':
        t.setStyleSheet(current_styles.menu)
    elif policy == 'bottom_button':
        t.setStyleSheet('QPushButton{background: transparent; border:none; padding:3px 3px; font-family:微软雅黑}'
                        'QPushButton:hover{background: lightgray}')
    elif policy == 'code_widget':
        t.update()
        print('update ------- ', t)
        t.viewport().update()


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

    def after_init(self, *a, **kw):
        current_styles.add_trace(self, _styled_policy, policy)
        _styled_policy(self, policy)

    class StyledFactory(object):
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__()
            cls.__init__ = _after(cls, '__init__')(after_init)

    return StyledFactory


T = t.TypeVar('T')


def make_styled(widget_clz: t.Type[T], policy, *a, **kw) -> T:
    obj = widget_clz(*a, **kw)
    current_styles.add_trace(obj, _styled_policy, policy)
    _styled_policy(obj, policy)
    return obj
