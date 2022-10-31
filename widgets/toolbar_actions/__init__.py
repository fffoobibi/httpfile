from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

toolbar_actions_controls = {}


def register(tool_tip: str, index: int = 0, icon: str = None):
    def wrapper(clz):
        toolbar_actions_controls[clz] = {'tool_tip': tool_tip, 'icon': icon, 'index': index}
        return clz

    return wrapper


def load_toolbar_actions():
    from pathlib import Path
    from importlib import import_module
    dir_path = Path(__file__).parent
    for path_ in dir_path.iterdir():
        if path_.name.startswith('toolbar_'):
            file, _ = path_.name.split('.')
            import_module(f'.{file}', 'widgets.toolbar_actions')
    return toolbar_actions_controls


class ToolBarActionMixIn(object):
    def __init__(self, main_app):
        self.app = main_app

    def make_action(self, icon_path, tool_tip, parent):
        return QAction(QIcon(icon_path), tool_tip, parent)

    def action_slot(self):
        pass
