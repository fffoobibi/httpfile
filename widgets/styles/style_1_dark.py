from . import register, BaseStyle


@register('dark', index=0)
class DarkStyle(BaseStyle):
    ## qss format
    menu = """
            QMenu{background: #333231;border:1px solid #434241}
            QMenu::item{
              padding:3px 20px;
              color:lightgray;
              font-size:9pt;
              font-family:微软雅黑}
            QMenu::item:hover{
              background-color:#242220;
            }
            QMenu::item:selected{
              background-color:#242220;} """

    ## json format
    editor_http_file = {
        'font': dict(request=None,
                     header=None,
                     data=None,
                     response=None,
                     key=None,
                     request_url=None,
                     splitter=None,
                     black=None,
                     section=None,
                     chinese=None,
                     output=None,
                     variable=None),
        'paper': dict(request='#1B1A19',
                      header='#1B1A19',
                      data='#1B1A19',
                      response='#1B1A19',
                      key='#1B1A19',
                      request_url='#1B1A19',
                      splitter='#1B1A19',
                      black='#1B1A19',
                      section='#1B1A19',
                      chinese='#1B1A19',
                      output='#1B1A19',
                      variable='#1B1A19'),
        'color': dict(request=None,
                      header='#9896FF',
                      data=None,
                      response='#9896FF',
                      key='#E55630',
                      request_url='#FFD866',
                      splitter=None,
                      black='#9896FF',
                      section='#9896FF',
                      chinese=None,
                      output=None,
                      variable='#FFD866'),
    }
