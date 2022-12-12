from PyQt5.Qsci import QsciLexerBatch, QsciLexerJavaScript, QsciLexerXML, QsciLexerMarkdown
from PyQt5.Qsci import QsciLexerJSON
from PyQt5.Qsci import QsciLexerPython
from PyQt5.Qsci import QsciLexerSQL

from . import register, BaseStyle


@register('vscode_dark', index=2)
class VsCodeDarkStyle(BaseStyle):
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
                 background: #323232;
                 color: lightgray;
                 border: 0px solid #C4C4C3;
                 border-bottom-color: #094770;
                 border-top-left-radius: 4px;
                 border-top-right-radius: 4px;
                 border-radius: 0px;
                 padding: 5px 10px;
             }
            QTabBar::tab:hover{background: #212121;}
            QTabBar::tab:selected{
                /*选中tab背景色*/
                background-color: #171615;
                color:#4484BA;
                border-top:2px solid transparent;
                border-bottom: 2px solid #094770
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
                QSplitter::handle:pressed {background-color:#094770;}"""
    progress = "QProgressBar {border: 0px solid grey; border-radius: 0px; background-color: #FFFFFF; text-align: center;}" \
               "QProgressBar::chunk {background:QLinearGradient(x1:0,y1:0,x2:2,y2:0,stop:0 #666699,stop:1  #DB7093); }"

    border = '#393A3C'
    border_lighter = '#606060'

    foreground = '#BAB9B8'
    un_focus_foreground = 'gray'

    background_darker = '#242425'
    background_lighter = '#323232'

    title_background = background_lighter
    toolbar_background = background_lighter
    menubar_background = background_lighter

    handler = '#575758'
    hover = '#4C5052'

    button_hover = '#2D3B47'
    toolbar_hover = '#4C5052'
    item_selected = '#094770'

    guides_background = '#3B3B3B'
    guides_foreground = '#3B3B3B'

    bottom_button = dict(color='lightgray', checked='orange', background='#333231', background_checked='#242220')
    left_button = dict(color='lightgray', checked='orange', background='#333231', background_checked='#242220',
                       border_checked='orange')

    editor_globals = {
        'selection': dict(background="#264E77"),
        'caret': dict(background='white', foreground='#262626'),  # 光标颜色, 背景色
        'margin': dict(background='#1E1E1E', foreground='#A4A3A3', foldmargin='#1E1E1E'),
        'font': dict(default='Microsoft YaHei UI', jetbrain='JetBrains Mono'),
        'fold_markers': dict(background='gray', foreground='#1E1E1E'),
        'paper': dict(background='#1E1E1E'),
        'statics': dict(indic_ref='gray', indic_ref_class='#264E77', indic_ref_define='#9B3A24')
    }

    editor_http_file = {
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
        'font': dict(default='JetBrains Mono'),
        'color': {
            QsciLexerJSON.Default: "lightgray",  # =
            QsciLexerJSON.Number: "#0078D7",  # = ...  # type: int
            QsciLexerJSON.String: "#CD9069",  # = ...  # type: int
            QsciLexerJSON.UnclosedString: "#CD9069",  # = ...  # type: int
            QsciLexerJSON.Property: "#61BCFB",  # = ...  # type: int
            QsciLexerJSON.EscapeSequence: "#57D1EB",  # = ...  # type: int, 转义符
            QsciLexerJSON.CommentLine: "gray",  # = ...  # type: int
            QsciLexerJSON.CommentBlock: "gray",  # = ...  # type: int
            QsciLexerJSON.Operator: "white",  # = ...  # type: int
            QsciLexerJSON.IRI: "#FFD866",  # = ...  # type: int
            QsciLexerJSON.IRICompact: "#FFD866",  # = ...  # type: int
            QsciLexerJSON.Keyword: "#00D3E9",  # = ...  # type: int
            QsciLexerJSON.KeywordLD: "#7C79FA",  # = ...  # type: int
            QsciLexerJSON.Error: "red",  # = ...  # type: int
            32: 'lightgray'  # 折叠线
        }
    }

    editor_sql = {
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
        'font': dict(default='JetBrains Mono'),  # JetBrains Mono
        'color': {
            QsciLexerPython.Default: '#C8CDCB',  # = ...  # type: int
            QsciLexerPython.Comment: '#5B9140',  # = ...  # type: int
            QsciLexerPython.Number: '#B4CDA8',  # = ...  # type: int
            QsciLexerPython.DoubleQuotedString: '#CD9069',  # = ...  # type: int
            QsciLexerPython.SingleQuotedString: '#CD9069',  # = ...  # type: int
            QsciLexerPython.Keyword: '#529CD3',  # = ...  # type: int
            QsciLexerPython.TripleSingleQuotedString: '#CD9069',  # = ...  # type: int
            QsciLexerPython.TripleDoubleQuotedString: '#CD9069',  # = ...  # type: int
            QsciLexerPython.ClassName: '#39C8B0',  # = ...  # type: int
            QsciLexerPython.FunctionMethodName: '#BCDB84',  # = ...  # type: int
            QsciLexerPython.Operator: '#A97CF8',  # = ...  # type: int
            QsciLexerPython.Identifier: '#D4D4D4',  # = ...  # type: int
            QsciLexerPython.CommentBlock: '#5B9140',  # = ...  # type: int
            QsciLexerPython.UnclosedString: '#FFD866',  # = ...  # type: int
            QsciLexerPython.HighlightedIdentifier: 'red',  # = ...  # type: int
            QsciLexerPython.Decorator: '#39C8B0',  # = ...  # type: int
            QsciLexerPython.DoubleQuotedFString: '#CD9069',  # = ...  # type: int
            QsciLexerPython.SingleQuotedFString: '#CD9069',  # = ...  # type: int
            QsciLexerPython.TripleSingleQuotedFString: '#CD9069',  # = ...  # type: int
            QsciLexerPython.TripleDoubleQuotedFString: '#CD9069',  # = ...  # type: int
            32: 'lightgray'  # 折叠线
        }
    }

    editor_javascript = {
        'color': {
            QsciLexerJavaScript.Default: "white",  # = ...  # type: int
            QsciLexerJavaScript.InactiveDefault: "red",  # = ...  # type: int
            QsciLexerJavaScript.Comment: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.InactiveComment: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.CommentLine: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.InactiveCommentLine: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.CommentDoc: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.InactiveCommentDoc: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.Number: "#00A4EF",  # = ...  # type: int 蓝色
            QsciLexerJavaScript.InactiveNumber: "#00A4EF",  # = ...  # type: int
            QsciLexerJavaScript.Keyword: "#ED6748",  # = ...  # type: int 橘色
            QsciLexerJavaScript.InactiveKeyword: "#ED6748",  # = ...  # type: int
            QsciLexerJavaScript.DoubleQuotedString: "#FFC56A",  # = ...  # type: int 浅黄色
            QsciLexerJavaScript.InactiveDoubleQuotedString: "#FFC56A",  # = ...  # type: int
            QsciLexerJavaScript.SingleQuotedString: "#FFC56A",  # = ...  # type: int
            QsciLexerJavaScript.InactiveSingleQuotedString: "#FFC56A",  # = ...  # type: int
            QsciLexerJavaScript.UUID: "",  # = ...  # type: int
            QsciLexerJavaScript.InactiveUUID: "red",  # = ...  # type: int
            QsciLexerJavaScript.PreProcessor: "red",  # = ...  # type: int
            QsciLexerJavaScript.InactivePreProcessor: "red",  # = ...  # type: int
            QsciLexerJavaScript.Operator: "#B6B3EB",  # = ...  # type: int 紫色
            QsciLexerJavaScript.InactiveOperator: "blue",  # = ...  # type: int
            QsciLexerJavaScript.Identifier: "#92D923",  # = ...  # type: int
            QsciLexerJavaScript.InactiveIdentifier: "red",  # = ...  # type: int
            QsciLexerJavaScript.UnclosedString: "",  # = ...  # type: int
            QsciLexerJavaScript.InactiveUnclosedString: "",  # = ...  # type: int
            QsciLexerJavaScript.VerbatimString: "",  # = ...  # type: int
            QsciLexerJavaScript.InactiveVerbatimString: "",  # = ...  # type: int
            QsciLexerJavaScript.Regex: "#FFC56A",  # = ...  # type: int
            QsciLexerJavaScript.InactiveRegex: "#FFC56A",  # = ...  # type: int
            QsciLexerJavaScript.CommentLineDoc: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.InactiveCommentLineDoc: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.KeywordSet2: "red",  # = ...  # type: int
            QsciLexerJavaScript.InactiveKeywordSet2: "red",  # = ...  # type: int
            QsciLexerJavaScript.CommentDocKeyword: "",  # = ...  # type: int
            QsciLexerJavaScript.InactiveCommentDocKeyword: "",  # = ...  # type: int
            QsciLexerJavaScript.CommentDocKeywordError: "",  # = ...  # type: int
            QsciLexerJavaScript.InactiveCommentDocKeywordError: "",  # = ...  # type: int
            QsciLexerJavaScript.GlobalClass: "#6FD6F9",  # = ...  # type: int
            QsciLexerJavaScript.InactiveGlobalClass: "red",  # = ...  # type: int
            QsciLexerJavaScript.RawString: "#FD971F",  # = ...  # type: int
            QsciLexerJavaScript.InactiveRawString: "#FD971F",  # = ...  # type: int
            QsciLexerJavaScript.TripleQuotedVerbatimString: "#FD971F",  # = ...  # type: int
            QsciLexerJavaScript.InactiveTripleQuotedVerbatimString: "#FD971F",  # = ...  # type: int
            QsciLexerJavaScript.HashQuotedString: "#FD971F",  # = ...  # type: int
            QsciLexerJavaScript.InactiveHashQuotedString: "#FD971F",  # = ...  # type: int
            QsciLexerJavaScript.PreProcessorComment: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.InactivePreProcessorComment: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.PreProcessorCommentLineDoc: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.InactivePreProcessorCommentLineDoc: "lightgray",  # = ...  # type: int
            QsciLexerJavaScript.UserLiteral: "red",  # = ...  # type: int
            QsciLexerJavaScript.InactiveUserLiteral: "",  # = ...  # type: int
            QsciLexerJavaScript.TaskMarker: "",  # = ...  # type: int
            QsciLexerJavaScript.InactiveTaskMarker: "",  # = ...  # type: int
            QsciLexerJavaScript.EscapeSequence: "#FFBDCE",  # = ...  # type: int 粉色
            QsciLexerJavaScript.InactiveEscapeSequence: "#FFBDCE",  # = ...  # type: int

        }}

    editor_html = {
        'color': {
            QsciLexerXML.ASPAtStart: "#CABBAB",  # ,=15
            QsciLexerXML.ASPJavaScriptComment: "#CABBAB",  # , = 57
            QsciLexerXML.ASPJavaScriptCommentDoc: "#CABBAB",  # , = 59
            QsciLexerXML.ASPJavaScriptCommentLine: "#CABBAB",  # , = 58
            QsciLexerXML.ASPJavaScriptDefault: "#CABBAB",  # , = 56
            QsciLexerXML.ASPJavaScriptDoubleQuotedString: "#CABBAB",  # , = 63
            QsciLexerXML.ASPJavaScriptKeyword: "#CABBAB",  # , = 62
            QsciLexerXML.ASPJavaScriptNumber: "#CABBAB",  # , = 60
            QsciLexerXML.ASPJavaScriptRegex: "#CABBAB",  # , = 67
            QsciLexerXML.ASPJavaScriptSingleQuotedString: "#CABBAB",  # , = 64
            QsciLexerXML.ASPJavaScriptStart: "#CABBAB",  # , = 55
            QsciLexerXML.ASPJavaScriptSymbol: "#CABBAB",  # , = 65
            QsciLexerXML.ASPJavaScriptUnclosedString: "#CABBAB",  # , = 66
            QsciLexerXML.ASPJavaScriptWord: "#CABBAB",  # , = 61
            QsciLexerXML.ASPPythonClassName: "#CABBAB",  # , = 114
            QsciLexerXML.ASPPythonComment: "#CABBAB",  # , = 107
            QsciLexerXML.ASPPythonDefault: "#CABBAB",  # , = 106
            QsciLexerXML.ASPPythonDoubleQuotedString: "#CABBAB",  # , = 109
            QsciLexerXML.ASPPythonFunctionMethodName: "#CABBAB",  # , = 115
            QsciLexerXML.ASPPythonIdentifier: "#CABBAB",  # , = 117
            QsciLexerXML.ASPPythonKeyword: "#CABBAB",  # , = 111
            QsciLexerXML.ASPPythonNumber: "#CABBAB",  # , = 108
            QsciLexerXML.ASPPythonOperator: "#CABBAB",  # , = 116
            QsciLexerXML.ASPPythonSingleQuotedString: "#CABBAB",  # , = 110
            QsciLexerXML.ASPPythonStart: "#CABBAB",  # , = 105
            QsciLexerXML.ASPPythonTripleDoubleQuotedString: "#CABBAB",  # , = 113
            QsciLexerXML.ASPPythonTripleSingleQuotedString: "#CABBAB",  # , = 112
            QsciLexerXML.ASPStart: "#CABBAB",  # , = 16
            QsciLexerXML.ASPVBScriptComment: "#CABBAB",  # , = 82
            QsciLexerXML.ASPVBScriptDefault: "#CABBAB",  # , = 81
            QsciLexerXML.ASPVBScriptIdentifier: "#CABBAB",  # , = 86
            QsciLexerXML.ASPVBScriptKeyword: "#CABBAB",  # , = 84
            QsciLexerXML.ASPVBScriptNumber: "#CABBAB",  # , = 83
            QsciLexerXML.ASPVBScriptStart: "#CABBAB",  # , = 80
            QsciLexerXML.ASPVBScriptString: "#CABBAB",  # , = 85
            QsciLexerXML.ASPVBScriptUnclosedString: "#CABBAB",  # , = 87
            QsciLexerXML.ASPXCComment: "#CABBAB",  # , = 20
            QsciLexerXML.Attribute: "#71C9F5",  # , = 3
            QsciLexerXML.CDATA: "blue",  # , = 17
            QsciLexerXML.Default: "gray",  # , = 0
            QsciLexerXML.Entity: "red",  # , = 10
            QsciLexerXML.HTMLComment: "gray",  # , = 9
            QsciLexerXML.HTMLDoubleQuotedString: "#E9B647",  # , = 6
            QsciLexerXML.HTMLNumber: "#E9B647",  # , = 5
            QsciLexerXML.HTMLSingleQuotedString: "#E9B647",  # , = 7
            QsciLexerXML.HTMLValue: "#CABBAB",  # , = 19
            QsciLexerXML.JavaScriptComment: "#C3BAAB",  # , = 42
            QsciLexerXML.JavaScriptCommentDoc: "#C3BAAB",  # , = 44
            QsciLexerXML.JavaScriptCommentLine: "#C3BAAB",  # , = 43
            QsciLexerXML.JavaScriptDefault: "#C3BAAB",  # , = 41
            QsciLexerXML.JavaScriptDoubleQuotedString: "#C3BAAB",  # , = 48
            QsciLexerXML.JavaScriptKeyword: "#C3BAAB",  # , = 47
            QsciLexerXML.JavaScriptNumber: "#C3BAAB",  # , = 45
            QsciLexerXML.JavaScriptRegex: "#C3BAAB",  # , = 52
            QsciLexerXML.JavaScriptSingleQuotedString: "#C3BAAB",  # , = 49
            QsciLexerXML.JavaScriptStart: "#C3BAAB",  # , = 40
            QsciLexerXML.JavaScriptSymbol: "#C3BAAB",  # , = 50
            QsciLexerXML.JavaScriptUnclosedString: "#C3BAAB",  # , = 51
            QsciLexerXML.JavaScriptWord: "#C3BAAB",  # , = 46
            QsciLexerXML.OtherInTag: "#C3BAAB",  # , = 8
            QsciLexerXML.PHPComment: "#C3BAAB",  # , = 124
            QsciLexerXML.PHPCommentLine: "#C3BAAB",  # , = 125
            QsciLexerXML.PHPDefault: "#C3BAAB",  # , = 118
            QsciLexerXML.PHPDoubleQuotedString: "#C3BAAB",  # , = 119
            QsciLexerXML.PHPDoubleQuotedVariable: "#C3BAAB",  # , = 126
            QsciLexerXML.PHPKeyword: "#C3BAAB",  # , = 121
            QsciLexerXML.PHPNumber: "#C3BAAB",  # , = 122
            QsciLexerXML.PHPOperator: "#C3BAAB",  # , = 127
            QsciLexerXML.PHPSingleQuotedString: "#C3BAAB",  # , = 120
            QsciLexerXML.PHPStart: "#C3BAAB",  # , = 18
            QsciLexerXML.PHPVariable: "#C3BAAB",  # , = 123
            QsciLexerXML.PythonClassName: "#C3BAAB",  # , = 99
            QsciLexerXML.PythonComment: "#C3BAAB",  # , = 92
            QsciLexerXML.PythonDefault: "#C3BAAB",  # , = 91
            QsciLexerXML.PythonDoubleQuotedString: "#C3BAAB",  # , = 94
            QsciLexerXML.PythonFunctionMethodName: "#C3BAAB",  # , = 100
            QsciLexerXML.PythonIdentifier: "#C3BAAB",  # , = 102
            QsciLexerXML.PythonKeyword: "#C3BAAB",  # , = 96
            QsciLexerXML.PythonNumber: "#C3BAAB",  # , = 93
            QsciLexerXML.PythonOperator: "#C3BAAB",  # , = 101
            QsciLexerXML.PythonSingleQuotedString: "#C3BAAB",  # , = 95
            QsciLexerXML.PythonStart: "#C3BAAB",  # , = 90
            QsciLexerXML.PythonTripleDoubleQuotedString: "#C3BAAB",  # , = 98
            QsciLexerXML.PythonTripleSingleQuotedString: "#C3BAAB",  # , = 97
            QsciLexerXML.Script: "red",  # , = 14
            QsciLexerXML.SGMLBlockDefault: "#EBCB8B",  # , = 31
            QsciLexerXML.SGMLCommand: "#EBCB8B",  # , = 22
            QsciLexerXML.SGMLComment: "gray",  # , = 29
            QsciLexerXML.SGMLDefault: "#EBCB8B",  # , = 21
            QsciLexerXML.SGMLDoubleQuotedString: "red",  # , = 24
            QsciLexerXML.SGMLEntity: "red",  # , = 28
            QsciLexerXML.SGMLError: "green",  # , = 26
            QsciLexerXML.SGMLParameter: "#71C9F5",  # , = 23
            QsciLexerXML.SGMLParameterComment: "green",  # , = 30
            QsciLexerXML.SGMLSingleQuotedString: "green",  # , = 25
            QsciLexerXML.SGMLSpecial: "green",  # , = 27
            QsciLexerXML.Tag: "#E35730",  # , = 1
            QsciLexerXML.UnknownAttribute: "red",  # , = 4
            QsciLexerXML.UnknownTag: "#E35730",  # , = 2
            QsciLexerXML.VBScriptComment: "#C3BAAB",  # , = 72
            QsciLexerXML.VBScriptDefault: "#C3BAAB",  # , = 71
            QsciLexerXML.VBScriptIdentifier: "#C3BAAB",  # , = 76
            QsciLexerXML.VBScriptKeyword: "#C3BAAB",  # , = 74
            QsciLexerXML.VBScriptNumber: "#C3BAAB",  # , = 73
            QsciLexerXML.VBScriptStart: "#C3BAAB",  # , = 70
            QsciLexerXML.VBScriptString: "#C3BAAB",  # , = 75
            QsciLexerXML.VBScriptUnclosedString: "#C3BAAB",  # , = 77
            QsciLexerXML.XMLEnd: "#CABBAB",  # , = 13
            QsciLexerXML.XMLStart: "#CABBAB",  # , = 12
            QsciLexerXML.XMLTagEnd: "#CABBAB",
            32: 'lightgray'

        }  # , = 11
    }
    editor_xml = editor_html
    editor_svg = editor_html
    editor_common = {
        'color': {
        }}

    editor_markdown = {
        'color': {
            QsciLexerMarkdown.BlockQuote: 'red',  # = 15
            QsciLexerMarkdown.CodeBackticks: '#647379',  # = 19, like `x=1`
            QsciLexerMarkdown.CodeBlock: '#647379',  # = 21
            QsciLexerMarkdown.CodeDoubleBackticks: '#647379',  # = 20
            QsciLexerMarkdown.Default: 'white',  # = 0
            QsciLexerMarkdown.EmphasisAsterisks: '#647379',  # = 4
            QsciLexerMarkdown.EmphasisUnderscores: '#647379',  # = 5
            QsciLexerMarkdown.Header1: '#ED6B88',  # = 6
            QsciLexerMarkdown.Header2: '#83D7EC',  # = 7
            QsciLexerMarkdown.Header3: '#A9DC76',  # = 8
            QsciLexerMarkdown.Header4: '#A685F7',  # = 9
            QsciLexerMarkdown.Header5: '#FF8C00',  # = 10
            QsciLexerMarkdown.Header6: '#F9B336',  # = 11
            QsciLexerMarkdown.HorizontalRule: 'lightgray',  # = 17, 水平线
            QsciLexerMarkdown.Link: '#D9F0FF',  # = 18
            QsciLexerMarkdown.OrderedListItem: '#E1D6FC',  # = 14
            QsciLexerMarkdown.Prechar: 'green',  # = 12
            QsciLexerMarkdown.Special: 'red',  # = 1
            QsciLexerMarkdown.StrikeOut: 'green',  # = 16
            QsciLexerMarkdown.StrongEmphasisAsterisks: 'green',  # = 2
            QsciLexerMarkdown.StrongEmphasisUnderscores: 'green',  # = 3
            QsciLexerMarkdown.UnorderedListItem: '#E1D6FC',  # = 13
        }}

    editor_web_console = {
        'color': dict(
            http='#00A4EF',
            info_http='#FF6077',
            info_time='#B4DA82',
            info_status='red',
            fold_info='orange',
            normal='lightgray',
        )
    }

    editor_run_console = {
        'color': dict(
            normal='lightgray',
            file_info='#C6DBE9',
            line_info='#C6DBE9',
            file_trace='red'
        )}


import pyls
