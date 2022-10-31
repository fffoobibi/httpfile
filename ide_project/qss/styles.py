from enum import IntEnum


class Styles:
    none = ''
    dark = '''
    QWidget{background: #333231;color:#AFB1B3;font-family: 微软雅黑}
    
    #frame_3{border:none; border-right: 1px solid #666666}
    #frame_4{border:none; border-left: 1px solid #666666}
    #frame{border:none; border-bottom: 1px solid #666666}
    #textBrowser{border: 1px solid #666666;border-top:none;background: #171615;color:#AFB1B3}
    
    
    QToolTip{
        background: #434241;
        border: 1px solid #242220;
        color:white;
        padding: 3px 5px
        }
        
    QPushButton{border:none;padding-left:5px; padding-right:5px}
    QPushButton:hover{background:#2D2B29;}
    
    QTreeView::branch:closed:has-children{image:url(:/icon/箭头_列表向右.svg); height: 10px}
    QTreeView::branch:open:has-children{image:url(:/icon/箭头_列表展开(1).svg);height: 10px}
    QTreeView::item:selected{background:#242220;color:#FFB900}
    QTreeView{outline:0px; border:none;border-top:1px solid #4D4C4B;
        border-bottom: 1px solid #4D4C4B;border-right: 1px solid #4D4C4B}
    
    QsciScintilla{border:none;border-bottom: 1px solid #4D4C4B}
    
    QHeaderView{background:transparent}
    QHeaderView::section{
        font-size:10pt;                
        font-family: Microsoft YaHei; 
        color:#FFFFFF;                 
        background:transparent;            
        border:none;                   
        text-align:left; 
        padding-top: 2px;
    }
    QHeaderView::section:selected{
        color:red}
    
    QScrollBar:vertical {background: #1B1A19; padding: 0px;max-width: 10px;}
    QScrollBar::handle:vertical {background: #424241; min-height: 20px;}
    QScrollBar::handle:vertical:hover {background: #4C4B4A;}
    QScrollBar::handle:vertical:pressed {background: #4C4B4A;}
    QScrollBar::add-page:vertical {background: none;height:0px}
    QScrollBar::sub-page:vertical {background: none;height:0px}
    QScrollBar::add-line:vertical {background: none;height:0px}
    QScrollBar::sub-line:vertical {background: none;height:0px}
    QScrollBar::down-arrow:vertical{height:0px}
    QScrollBar::up-arrow:vertical{height:0px}
    
    QScrollBar:horizontal{background: #1B1A19; padding: 0px;max-height: 10px;}
    QScrollBar::handle:horizontal {background: #424241; min-width: 20px;}
    QScrollBar::handle:horizontal:hover {background: #4C4B4A;}
    QScrollBar::handle:horizontal:pressed {background: #4C4B4A;}
    QScrollBar::add-page:horizontal {background: none;width:0px}
    QScrollBar::sub-page:horizontal {background: none;width:0px}
    QScrollBar::add-line:horizontal {background: none; width:0px}
    QScrollBar::sub-line:horizontal {background: none;width:0px}
    QScrollBar::down-arrow:horizontal{background: none; width:0px}
    QScrollBar::up-arrow:horizontal{background: none; width:0px}
                    
    QTabWidget::pane{border:none;}
    QTabWidget{border: 1px solid #4D4C4B}      
    QTabWidget::tab-bar {left: 0px;}
    QTabBar::tab{
         background: #525151;
         color: #78DCE8;
         border: 0px solid #C4C4C3;
         border-bottom-color: #C2C7CB;
         border-top-left-radius: 4px;
         border-top-right-radius: 4px;
         min-height: 30px;
         border-radius: 0px;
         padding: 0px;
     }
    QTabBar::tab:hover{background: #2D2B29;}
    QTabBar::tab:selected{
        /*选中teble背景色*/
        background-color: #2D2B29;
        color:#80DC76;
        border-bottom: 2px solid #FFC800
    }
    '''
    light = ''


class MenuStyles(str):
    none = ''
    dark = '''
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
              background-color:#242220;
            }'''
    light = '''
            QMenu{background: #EEE9E9;border:1px solid white}
            QMenu::item{
              padding:3px 20px;
              color:black;
              font-size:9pt;
              font-family:微软雅黑}
            QMenu::item:hover{
              background-color:lightgray;
            }
            QMenu::item:selected{
              background-color:gray;
            }'''


class Themes(IntEnum):
    none = -1
    dark = 0
    light = 1
