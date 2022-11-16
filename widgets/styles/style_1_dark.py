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
        'font': dict(request=0,  # 1, 0b0001
                     header=1,  # 2, 0b0010
                     data=2,  # 4, 0b0100
                     response=3,
                     key=4,
                     request_url=5,
                     splitter=6,
                     black=7,
                     section=8,
                     chinese=12,
                     output=13,
                     variable=14, ),
        'paper': dict(request=0,  # 1, 0b0001
                      header=1,  # 2, 0b0010
                      data=2,  # 4, 0b0100
                      response=3,
                      key=4,
                      request_url=5,
                      splitter=6,
                      black=7,
                      section=8,
                      chinese=12,
                      output=13,
                      variable=14, ),
        'color': dict(request=0,  # 1, 0b0001
                      header=1,  # 2, 0b0010
                      data=2,  # 4, 0b0100
                      response=3,
                      key=4,
                      request_url=5,
                      splitter=6,
                      black=7,
                      section=8,
                      chinese=12,
                      output=13,
                      variable=14, ),
    }
