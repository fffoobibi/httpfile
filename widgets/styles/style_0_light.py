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
    tab = """"""
    foreground = 'lightgray'

    foreground = 'black'
    background_darker = 'white'
    background_lighter = 'white'
    handler = 'gray'
    bottom_button = dict(color='black', checked='black', background='transparent', background_checked='lightgray')
    left_button = dict(color='lightgray', checked='orange', background='#333231', background_checked='#242220', border_checked='orange')

    editor_http_file = dict(font={}, color={}, paper={}, margin={}, caret={}, selection={}, tooltip={})
    editor_web_console = {
        'font': {},
        'paper': dict(background='white'),
        'color': dict(
            http='#00A4EF',
            info_http='red',
            info_time='green',
            info_status='red',
            fold_info='black',
            normal='black',
        )
    }
