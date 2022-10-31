from PyQt5.QtGui import QFontDatabase


class AppConfig(object):
    _font_ids = {}

    def __init__(self):
        self._load_fonts()

    def _load_fonts(self):
        # jetbran_momo = r"C:\Users\fqk12\Desktop\pyqt5_pay_tool\ide_project\sources\jetbrains-mono\JetBrainsMono-Medium.ttf"
        jetbran_momo = r"C:\Users\admin\Desktop\新建文件夹\ide_project\sources\jetbrains-mono\JetBrainsMono-Medium.ttf"
        font_id = QFontDatabase.addApplicationFont(jetbran_momo)
        self._font_ids['jetbran_momo'] = font_id

    def get_momo_font(self):
        momo_id = self._font_ids.get('jetbran_momo', None)
        return QFontDatabase.applicationFontFamilies(momo_id)[0]
