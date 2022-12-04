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

    def when_remove(self):
        """"""


class ILanguageInterFace(Interface):
    def onTextDocumentInfer(self, word: str, line, col):
        """"""

    def onTextDocumentCompletion(self, word: str, line, col):
        """"""

    def onTextDocumentHover(self, word: str, line: int, col: int):
        """"""

    def onTextDocumentReferences(self, word: str, line, col):
        """"""

    def onTextDocumentRename(self, word: str, line, col):
        """"""

    def onTextDocumentSyntaxCheck(self, word: str, line, col):
        """"""
