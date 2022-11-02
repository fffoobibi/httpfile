from pathlib import Path
from collections import namedtuple

from widgets.bottom_control import load_control_widgets
from widgets.left_control import load_left_control_widgets
from widgets.tabs import load_tab_widgets
from widgets.toolbar_actions import load_toolbar_actions
# from widgets.status import load_status_control_widgets

from widgets.utils import ConfigProvider
from configs import configs

Collections = namedtuple('Collections', 'folder tabs controls left_controls toolbar_actions status')


def collect_plugins() -> Collections:
    ConfigProvider.register_configs(configs)
    # print(ConfigProvider._defaults)
    folder = Path.cwd().__str__()
    tabs = load_tab_widgets()
    controls = load_control_widgets()
    left_controls = load_left_control_widgets()
    toolbar_actions = load_toolbar_actions()
    # status_widgets = load_status_control_widgets()
    return Collections(folder=folder, tabs=tabs, controls=controls, left_controls=left_controls, toolbar_actions=toolbar_actions,
                       status={}
                       )
