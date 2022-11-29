from . import register, BaseStyle
from PyQt5.Qsci import QsciLexerJSON
from PyQt5.Qsci import QsciLexerPython
from PyQt5.Qsci import QsciLexerSQL
from PyQt5.Qsci import QsciLexerBatch, QsciLexerBash


@register('dark', index=0)
class DarkStyle(BaseStyle):
    ## qss format
    tooltip = """QToolTip{border:1px solid gray; background-color:#333231;color:lightgray;padding:4px}"""
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
    handler = '#5D5C5B'
    hover = 'red'

    guides_background = '#333231'
    guides_foreground = '#333231'

    bottom_button = dict(color='lightgray', checked='orange', background='#333231', background_checked='#242220')
    left_button = dict(color='lightgray', checked='orange', background='#333231', background_checked='#242220',
                       border_checked='orange')
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

    editor_json = {
        'selection': dict(background="#323341"),
        'caret': dict(background='#FFD64C', foreground='#212131'),
        'margin': dict(background='#2D2B29', foreground='#666666'),
        'font': {},
        'paper': dict(background='#1B1A19'),
        'color': {
            QsciLexerJSON.Default: "lightgray",  # =
            QsciLexerJSON.Number: "#0078D7",  # = ...  # type: int
            QsciLexerJSON.String: "#FFD866",  # = ...  # type: int
            QsciLexerJSON.UnclosedString: "#FFD866",  # = ...  # type: int
            QsciLexerJSON.Property: "#7C79FA",  # = ...  # type: int
            QsciLexerJSON.EscapeSequence: "#57D1EB",  # = ...  # type: int, 转义符
            QsciLexerJSON.CommentLine: "gray",  # = ...  # type: int
            QsciLexerJSON.CommentBlock: "gray",  # = ...  # type: int
            QsciLexerJSON.Operator: "#FD971F",  # = ...  # type: int
            QsciLexerJSON.IRI: "#FFD866",  # = ...  # type: int
            QsciLexerJSON.IRICompact: "#FFD866",  # = ...  # type: int
            QsciLexerJSON.Keyword: "#00D3E9",  # = ...  # type: int
            QsciLexerJSON.KeywordLD: "#7C79FA",  # = ...  # type: int
            QsciLexerJSON.Error: "red",  # = ...  # type: int
            32: 'lightgray'  # 折叠线
        }
    }

    editor_sql = {
        'selection': dict(background="#323341"),
        'caret': dict(background='#FFD64C', foreground='#212131'),
        'margin': dict(background='#2D2B29', foreground='#666666'),
        'font': dict(default='Microsoft YaHei UI'),
        'paper': dict(background='#1B1A19'),
        'color': {
            QsciLexerSQL.Comment: 'lightgray',  # = 1
            QsciLexerSQL.CommentDoc: 'lightgray',  # = 3
            QsciLexerSQL.CommentDocKeyword: 'lightgray',  # = 17
            QsciLexerSQL.CommentDocKeywordError: 'red',  # = 18
            QsciLexerSQL.CommentLine: 'lightgray',  # = 2
            QsciLexerSQL.CommentLineHash: 'lightgray',  # = 15
            QsciLexerSQL.Default: 'white',  # = 0
            QsciLexerSQL.DoubleQuotedString: '#FFD866',  # = 6
            QsciLexerSQL.Identifier: '#7976F9',  # = 11 紫色
            QsciLexerSQL.Keyword: '#EA5831',  # = 5
            QsciLexerSQL.KeywordSet5: '',  # = 19
            QsciLexerSQL.KeywordSet6: '',  # = 20
            QsciLexerSQL.KeywordSet7: '',  # = 21
            QsciLexerSQL.KeywordSet8: '',  # = 22
            QsciLexerSQL.Number: '#0B74BC',  # = 4
            QsciLexerSQL.Operator: '#4DC4FF',  # = 10 括号
            QsciLexerSQL.PlusComment: '',  # = 13
            QsciLexerSQL.PlusKeyword: '',  # = 8
            QsciLexerSQL.PlusPrompt: '',  # = 9
            QsciLexerSQL.QuotedIdentifier: 'red',  # = 23
            QsciLexerSQL.QuotedOperator: 'red',  # = 24
            QsciLexerSQL.SingleQuotedString: '#FFD866',  # = 7 注释,字符串
        }
    }

    editor_batch = {
        'selection': dict(background="#323341"),
        'caret': dict(background='#FFD64C', foreground='#212131'),
        'margin': dict(background='#2D2B29', foreground='#666666'),
        'font': dict(default='Microsoft YaHei UI'),
        'paper': dict(background='#1B1A19'),
        'color': {
            QsciLexerBatch.Comment: "lightgray",  # = 1
            QsciLexerBatch.Default: "#56B622",  # = 0
            QsciLexerBatch.ExternalCommand: "red",  # = 5
            QsciLexerBatch.HideCommandChar: "#56B622",  # = 4
            QsciLexerBatch.Keyword: "#EA5831",  # = 2
            QsciLexerBatch.Label: "#56B622",  # = 3
            QsciLexerBatch.Operator: "#4DC4FF",  # = 7
            QsciLexerBatch.Variable: "#FFD866",  # = 6
        }
    }

    editor_python = {
        'selection': dict(background="#323341"),
        'caret': dict(background='#FFD64C', foreground='#212131'),
        'margin': dict(background='#2D2B29', foreground='#666666'),
        'font': dict(default='Microsoft YaHei UI', jetbrain='JetBrains Mono Medium'),
        'paper': dict(background='#1B1A19'),
        'color': {
            QsciLexerPython.Default: '#F8F5ED',  # = ...  # type: int
            QsciLexerPython.Comment: 'lightgray',  # = ...  # type: int
            QsciLexerPython.Number: '#0078D7',  # = ...  # type: int
            QsciLexerPython.DoubleQuotedString: '#FFD866',  # = ...  # type: int
            QsciLexerPython.SingleQuotedString: '#FFD866',  # = ...  # type: int
            QsciLexerPython.Keyword: '#EE7762',  # = ...  # type: int
            QsciLexerPython.TripleSingleQuotedString: '#FFD866',  # = ...  # type: int
            QsciLexerPython.TripleDoubleQuotedString: '#FFD866',  # = ...  # type: int
            QsciLexerPython.ClassName: '#70D7FF',  # = ...  # type: int
            QsciLexerPython.FunctionMethodName: '#91CA1D',  # = ...  # type: int
            QsciLexerPython.Operator: '#A97CF8',  # = ...  # type: int
            QsciLexerPython.Identifier: '#F8F5ED',  # = ...  # type: int
            QsciLexerPython.CommentBlock: 'lightgray',  # = ...  # type: int
            QsciLexerPython.UnclosedString: '#FFD866',  # = ...  # type: int
            QsciLexerPython.HighlightedIdentifier: '',  # = ...  # type: int
            QsciLexerPython.Decorator: '#FD971F',  # = ...  # type: int
            QsciLexerPython.DoubleQuotedFString: '#FFD866',  # = ...  # type: int
            QsciLexerPython.SingleQuotedFString: '#FFD866',  # = ...  # type: int
            QsciLexerPython.TripleSingleQuotedFString: '#FFD866',  # = ...  # type: int
            QsciLexerPython.TripleDoubleQuotedFString: '#FFD866',  # = ...  # type: int
            32: 'lightgray'  # 折叠线
        }
    }

    editor_html = {
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
