from widgets.utils import ConfigKey
from pathlib import Path

configs = {
    ConfigKey.general: dict(single_step=8, horizontal_height=12, vertical_width=12, handler_color='#CFCFCF', handler_background='transparent'),
    ConfigKey.left_control_virtualtree: dict(work_path=Path.cwd().__str__()),
    ConfigKey.http_code_widget: dict(output_headers=True, output_response=True, output_runinfo=True)
}
