import typing as t
from functools import wraps

from PyQt5.QtGui import QPalette, QColor

from widgets.styles import current_styles


def _styled_policy(t, policy, *a):
    if policy == 'menu':
        if hasattr(t, 'render_custom_style'):
            t.render_custom_style()
        else:
            t.setStyleSheet(current_styles.menu)
    elif policy == 'qApp':
        t.setStyleSheet(current_styles.tooltip)
    elif policy == 'splitter':
        t.setStyleSheet(current_styles.splitter or '')
    elif policy == 'code_widget':  # editor wiget
        if hasattr(t, 'render_custom_style'):
            t.render_custom_style()
    elif policy == 'tab':  # tabwidget
        if hasattr(t, 'render_custom_style'):
            t.render_custom_style()
        else:
            t.setStyleSheet(current_styles.tab)
    elif policy == 'run-tab':
        if hasattr(t, 'render_custom_style'):
            t.render_custom_style()
        else:
            t.setStyleSheet(current_styles.run_tab)
    elif policy == 'background-darker':  # widget background
        if hasattr(t, 'render_custom_style'):
            t.render_custom_style()
        else:
            t.setAutoFillBackground(True)
            palette = t.palette()  # type: QPalette
            palette.setColor(QPalette.Window, QColor(current_styles.background_darker))
            palette.setColor(QPalette.Foreground, QColor(current_styles.foreground))
            t.setPalette(palette)
        t.update()
    elif policy == 'background-lighter':  # widget background
        palette = t.palette()  # type: QPalette
        palette.setColor(QPalette.Background, QColor(current_styles.background_lighter))
    elif policy == 'status-bar':
        t.setStyleSheet('''
            QStatusBar::item {border: 0px;}
            QStatusBar{background: %s;}
        ''' % current_styles.background_lighter)
    elif policy in ['bottom-button', 'status-button']:  # bottom buttons, status buttons
        color = current_styles.bottom_button.get('color')
        background = current_styles.bottom_button.get('background')
        background_checked = current_styles.bottom_button.get('background_checked')
        t.setStyleSheet('QPushButton{background: %s;border:none;padding:4px;font-family:微软雅黑;color:%s}'
                        'QPushButton:hover{background: %s;}'
                        'QPushButton:checked{background: %s}' % (
                            background, color, background_checked, background_checked
                        ))
    elif policy == 'left-button':  # left buttons
        color = current_styles.left_button.get('color')
        background = current_styles.left_button.get('background')
        background_checked = current_styles.left_button.get('background_checked')
        border_checked = current_styles.left_button.get('border_checked')
        t.setStyleSheet('QPushButton{background: %s;border:none;font-family:微软雅黑;color:%s;padding:8px}'
                        'QPushButton:hover{background: %s;}'
                        'QPushButton:checked{background: %s;border-left:1px solid %s;border-right:1px solid %s}' % (
                            background, color, background_checked, background_checked, border_checked, background_checked))
    elif policy == 'run-button':
        color = current_styles.left_button.get('color')
        background = current_styles.left_button.get('background')
        background_checked = current_styles.left_button.get('background_checked')
        border_checked = current_styles.left_button.get('border_checked')
        t.setStyleSheet('QPushButton{background: %s;border:none;font-family:微软雅黑;color:%s;padding:2px 10px}'
                        'QPushButton:hover{background: %s;}'
                        'QPushButton:checked{background: %s;border-bottom:1px solid %s;border-right:1px solid %s}' % (
                            background, color, background_checked, background_checked, border_checked, background_checked))


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

    class _StyledFactory(object):
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__()
            cls.__init__ = _after(cls, '__init__')(after_init)

    return _StyledFactory


T = t.TypeVar('T')


def make_styled(widget_clz: t.Type[T], policy, *a, **kw) -> T:
    obj = widget_clz(*a, **kw)
    current_styles.add_trace(obj, _styled_policy, policy)
    _styled_policy(obj, policy)
    return obj


def add_styled(obj: T, policy) -> T:
    current_styles.add_trace(obj, _styled_policy, policy)
    _styled_policy(obj, policy)
    return obj
