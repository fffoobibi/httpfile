from pyqt5utils.components.styles import StylesHelper
from widgets.base import PluginBaseMixIn
from widgets.utils import ConfigProvider, ConfigKey

tab_codes = {}


def register(file_types: list):
    def wrapper(clz):
        tab_codes[clz] = [f'{f} File' if f else 'File' for f in file_types]
        return clz

    return wrapper


def load_tab_widgets():
    from pathlib import Path
    from importlib import import_module
    dir_path = Path(__file__).parent
    for path_ in dir_path.iterdir():
        if path_.name.startswith('tab_'):
            file, _ = path_.name.split('.')
            import_module(f'.{file}', 'widgets.tabs')
    return tab_codes


class TabCodeMixIn(PluginBaseMixIn):
    single_step = ConfigProvider.default(ConfigKey.general, 'single_step')
    horizontal = ConfigProvider.default(ConfigKey.general, 'horizontal_height')
    vertical = ConfigProvider.default(ConfigKey.general, 'vertical_width')

    def _after_init(self):
        StylesHelper.set_v_history_style_dynamic(self, color='#CFCFCF', background='transparent',
                                                 width=self.vertical.value)
        StylesHelper.set_h_history_style_dynamic(self, color='#CFCFCF', background='transparent',
                                                 height=self.horizontal.value)
        self.setStyleSheet('border:none')
