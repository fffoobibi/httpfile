from . import register, BaseStyle


@register('dark', index=0)
class DarkStyle(BaseStyle):
    ## qss format
    tooltip = """QToolTip{border:1px solid gray; background-color:#4D4C4B;color:lightgray;padding:4px}"""
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
    tab = """
            QTabWidget::pane{border:none;}
            QTabWidget{border: 1px solid #4D4C4B}      
            QTabWidget::tab-bar {left: 0px;}
            QTabBar::close-button {
                image:url(:/icon/关闭-tab.svg)
            }
            QTabBar::close-button:selected {
                image: url(:/icon/关闭-tab.svg)
            }
            QTabBar::close-button:selected:hover {
                image: url(:/icon/关闭实心-tab.svg)
            }
            QTabBar::tab{
                 background: #333231;
                 color: lightgray;
                 border: 0px solid #C4C4C3;
                 border-bottom-color: #C2C7CB;
                 border-top-left-radius: 4px;
                 border-top-right-radius: 4px;
                 border-radius: 0px;
                 padding: 5px 10px;
             }
            QTabBar::tab:hover{background: #2D2B29;}
            QTabBar::tab:selected{
                /*选中teble背景色*/
                background-color: #171615;
                color:#78DCE8;
                border-top:2px solid transparent;
                border-bottom: 2px solid #FFC800
            }
    """
    run_tab = """
            QTabBar{font-family:微软雅黑}
            QTabBar::close-button {
                image:url(:/icon/关闭-tab.svg)
            }
            QTabBar::close-button:selected {
                image: url(:/icon/关闭-tab.svg)
            }
            QTabBar::close-button:selected:hover {
                image: url(:/icon/关闭实心-tab.svg)
            }
            QTabBar::tab{
                 background: #2D2B29; 
                 color: lightgray;
                 border: 0px solid #C4C4C3;
                 border-bottom-color: #DD6F13;
                 border-top-left-radius: 4px;
                 border-top-right-radius: 4px;
                 border-radius: 0px;
                 padding: 5px 3px;
             }
            QTabBar::tab:hover{background: #2D2B29;}
            QTabBar::tab:selected{
                background-color: #171615;
                color:#DD6F13;
                border-top: 1px solid  #171615;
                border-bottom: 1px solid #DD6F13
            }
    """
    splitter = """
                QSplitter::handle{background:transparent}
                QSplitter::handle:pressed {background-color:orange;}"""
    progress = "QProgressBar {border: 0px solid grey; border-radius: 0px; background-color: #FFFFFF; text-align: center;}" \
               "QProgressBar::chunk {background:QLinearGradient(x1:0,y1:0,x2:2,y2:0,stop:0 #666699,stop:1  #DB7093); }"

    border = '#4D4C4B'
    border_lighter = 'gray'

    foreground = 'lightgray'
    background_darker = '#333231'
    background_lighter = '#434241'
    handler = '#4C4B4A'
    bottom_button = dict(color='lightgray', checked='orange', background='#333231', background_checked='#242220')
    left_button = dict(color='lightgray', checked='orange', background='#333231', background_checked='#242220', border_checked='orange')
    editor_http_file = {
        'tooltip': dict(background='#2D2B29', foreground='lightgray'),
        'selection': dict(background="#323341"),
        'caret': dict(background='#FFD64C', foreground='#212131'),
        'margin': dict(background='#2D2B29', foreground='#666666'),
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

    editor_web_console = {
        'font': {},
        'paper': dict(background='#1B1A19'),
        'color': dict(
            http='#00A4EF',
            info_http='#FF6077',
            info_time='#B4DA82',
            info_status='red',
            fold_info='orange',
            normal='lightgray',
        )
    }

    editor_run_console = {'font': {},
                          'paper': dict(background='#1B1A19'),
                          'color': dict(
                              normal='lightgray',
                              file_info='#C6DBE9',
                              line_info='#C6DBE9',
                              file_trace='red'
                          )}
