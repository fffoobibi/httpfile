from PyQt5.QtWidgets import QWidget, QHBoxLayout
from contextlib import suppress

try:
    from qtconsole.rich_jupyter_widget import RichIPythonWidget
    from qtconsole.manager import QtKernelManager
    from qtconsole.inprocess import QtInProcessKernelManager

    from ipykernel.inprocess.ipkernel import InProcessInteractiveShell

    # The ID of an installed kernel, e.g. 'bash' or 'ir'.
    USE_KERNEL = 'python3'


    class _IPython(RichIPythonWidget):

        def __init__(self, banner_text: str = None, style: str = None):
            super(_IPython, self).__init__()
            self._shell = None
            self.banner_text = banner_text

            if style:
                self.set_default_style(style)

        def _handle_error(self, msg):
            from conf_log import APP_LOGGER
            APP_LOGGER.info('get msg: %s' % msg['content'])
            super()._handle_error(msg)

        @property
        def shell(self) -> 'InProcessInteractiveShell':
            if self._shell is None:
                self._shell = self.kernel_manager.kernel.shell
            return self._shell

        def _banner_default(self):
            return self.banner_text or 'Welcome to baizhou shell\n'

        def shutdown_kernel(self):
            self.kernel_client.stop_channels()
            self.kernel_manager.shutdown_kernel()

    class IPythonWidget(QWidget):
        def __init__(self, banner_text: str = None, style: str = None):
            super(IPythonWidget, self).__init__()
            self._ipython = _make_ipython_widget_with_kernel(banner_text, style)
            lay = QHBoxLayout(self)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(self._ipython)

        @property
        def ipython(self):
            return self._ipython

        def closeEvent(self, a0) -> None:
            super(IPythonWidget, self).closeEvent(a0)
            with suppress(Exception):
                self._ipython.shutdown_kernel()

        def close(self):
            super(IPythonWidget, self).close()
            with suppress(Exception):
                self._ipython.shutdown_kernel()


    def _make_ipython_widget_with_kernel(banner_text: str = None, style: str = None):
        """Start a kernel, connect to it, and create a RichJupyterWidget to use it
        """
        # kernel_manager = QtKernelManager(kernel_name=USE_KERNEL)
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        ipython_widget = _IPython(banner_text, style)
        ipython_widget.kernel_manager = kernel_manager
        ipython_widget.kernel_client = kernel_client

        # ipython_widget._handle_error()

        # ipython_widget.set_default_style('linux')
        # ipython_widget.input_buffer = 'gggggg'
        # ipython_widget.in_prompt = '>> '
        # ipython_widget.kernel_manager.kernel_restarted
        # ipython_widget._set_font(QFont('微软雅黑'))
        # ipython_widget._append_custom(0, "sdddd", )

        def hello():
            print(111)

        # ipython_widget.shell.push({'hello': hello})

        return ipython_widget

except ImportError:
    from conf_log import APP_LOGGER
    import traceback

    APP_LOGGER.warn('import qtconsole fail: %s' % traceback.print_exc())
    IPythonWidget = None

__all__ = (
    'IPythonWidget'
)

# class MainWindow(QtWidgets.QMainWindow):
#     """A window that contains a single Qt console."""
#
#     def __init__(self):
#         super().__init__()
#         self.jupyter_widget = make_jupyter_widget_with_kernel()
#         # self.jupyter_widget._banner_default
#         self.setCentralWidget(self.jupyter_widget)
#         # self.jupyter_widget.clear_output()
#         # self.jupyter_widget.clear_on_kernel_restart
#         print(self.jupyter_widget.kernel_banner)
#
#     def shutdown_kernel(self):
#         print('Shutting down kernel...')
#         self.jupyter_widget.kernel_client.stop_channels()
#         self.jupyter_widget.kernel_manager.shutdown_kernel()
#
#
# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     app.aboutToQuit.connect(window.shutdown_kernel)
#     sys.exit(app.exec_())
