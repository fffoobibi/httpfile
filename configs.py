from widgets.utils import ConfigKey
from pathlib import Path

configs = {
    ConfigKey.left_control_virtualtree: dict(work_path=Path.cwd().__str__())
}
