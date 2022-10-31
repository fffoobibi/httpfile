from widgets.utils import ConfigKey
from pathlib import Path

configs = {
    ConfigKey.general: dict(single_step=8, horizontal_height=12, vertical_width=12),
    ConfigKey.left_control_virtualtree: dict(work_path=Path.cwd().__str__())
}
