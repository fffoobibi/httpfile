from . import register, BaseStyle


@register('light', index=0)
class LightStyle(BaseStyle):
    menu = """
            QMenu{
              background:white;
              border:1px solid lightgray;
            }
            QMenu::item{
              padding:3px 20px;
              color:rgba(51,51,51,1);
              font-size:9pt;
              font-family:微软雅黑
            }
            QMenu::item:hover{
              background-color:rgb(236,236,237);
            }
            QMenu::item:selected{
              background-color:rgb(236,236,237);
            }"""
