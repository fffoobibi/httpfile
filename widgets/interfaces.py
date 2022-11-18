from zope.interface import Interface, Attribute


class IRenderStyle(Interface):
    def render_custom_style(self):
        """颜色渲染"""


class ITabInterFace(IRenderStyle):
    is_remote = Attribute('是否是远程文件')
    file_loaded = Attribute('加载完成信号')

    def load_file(self, file_path, content: str = None):
        """加载文件"""

    def file_path(self) -> str:
        """文件路径"""

    def set_read_only(self, v: bool):
        """设置编码方式"""
