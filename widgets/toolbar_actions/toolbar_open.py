from pathlib import Path

from PyQt5.QtWidgets import QFileDialog

from widgets.signals import signal_manager
from . import register, ToolBarActionMixIn

index = 1
icon = ':/icon/文件夹.svg'


@register('打开...', index=index, icon=icon)
class OpenAction(ToolBarActionMixIn):

    def action_slot(self):
        current = Path.cwd()
        out = QFileDialog.getExistingDirectory(self.app, '打开文件夹', current.__str__())
        if out:
            signal_manager.emit(signal_manager.loadProject, out)
            # self.app.load_dir_path(out)
