from mainwidget import MainWidget


class MainWidgetHelper(object):
    def __init__(self, app: MainWidget):
        self.app = app

    def set_slots(self):
        self._set_bottom_buttons_slots()

    def _set_bottom_buttons_slots(self):
        def _bottom_btn_clicked(btn):
            pass

        self.app.bottom_groups.buttonClicked.connect()
