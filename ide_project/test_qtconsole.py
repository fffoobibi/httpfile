import sys
# from qtpy import QtWidgets
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont

from qtconsole.rich_jupyter_widget import RichJupyterWidget, RichIPythonWidget
from qtconsole.manager import QtKernelManager

# The ID of an installed kernel, e.g. 'bash' or 'ir'.
USE_KERNEL = 'python3'

"Traitlets"


def make_jupyter_widget_with_kernel():
    """Start a kernel, connect to it, and create a RichJupyterWidget to use it
    """
    kernel_manager = QtKernelManager(kernel_name=USE_KERNEL)
    kernel_manager.start_kernel()

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()

    # jupyter_widget = RichJupyterWidget()
    jupyter_widget = JupyterWidget()
    jupyter_widget.kernel_manager = kernel_manager
    jupyter_widget.kernel_client = kernel_client
    # jupyter_widget.set_default_style('linux')

    # jupyter_widget.input_buffer = 'gggggg'
    # jupyter_widget.in_prompt = '>> '

    # jupyter_widget.kernel_manager.kernel_restarted
    # # jupyter_widget._set_font(QFont('微软雅黑'))
    # jupyter_widget._append_custom(0, "sdddd", )
    return jupyter_widget


class JupyterWidget(RichJupyterWidget):
    def _banner_default(self):
        return "fuck you ,bitch\n"


class MainWindow(QtWidgets.QMainWindow):
    """A window that contains a single Qt console."""

    def __init__(self):
        super().__init__()
        self.jupyter_widget = make_jupyter_widget_with_kernel()
        self.setCentralWidget(self.jupyter_widget)
        print(self.jupyter_widget.kernel_banner)

    # def closeEvent(self, a0: 'QtGui.QCloseEvent') -> None:
    #     super().closeEvent(a0)
    #     self.shutdown_kernel()

    def shutdown_kernel(self):
        print('Shutting down kernel...')
        self.jupyter_widget.kernel_client.stop_channels()
        self.jupyter_widget.kernel_manager.shutdown_kernel()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # app.aboutToQuit.connect(window.shutdown_kernel)
    sys.exit(app.exec_())
