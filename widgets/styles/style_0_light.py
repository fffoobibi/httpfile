from PyQt5.Qsci import QsciLexerPython

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
    run_tab = """"""

    foreground = 'black'
    background_darker = '#F2F2F2'
    background_lighter = '#FFFFFF'

    title_background: str = background_darker
    menubar_background: str = background_darker
    toolbar_background: str = background_darker
    left_background: str = background_lighter

    handler = '#D8D8D8'
    border = '#D0D0D0'
    bottom_button = dict(color='black', checked='black', background='transparent', background_checked='lightgray')
    left_button = dict(color='lightgray', checked='orange', background=background_lighter,
                       background_checked=background_darker,
                       border_checked='red')

    editor_globals = {
        'selection': dict(background="#5974AB"),
        'caret': dict(background='black', foreground='#FFFAE3'),  # 光标颜色, 背景色
        'margin': dict(background='#F0F0F0', foreground='#9B9AA6', foldmargin='#F0F0F0'),
        'fold_markers': dict(background=border, foreground='white'),
        'font': dict(default='JetBrains Mono', jetbrain='JetBrains Mono', yahei='Microsoft YaHei UI'),
        'paper': dict(background='#FFFFFF'),
        'statics': dict(indic_ref='gray', indic_ref_class='#264E77', indic_ref_define='#9B3A24')
    }

    editor_python = {
        'font': dict(default='JetBrains Mono'),  # JetBrains Mono
        'color': {
            QsciLexerPython.Default: 'black',  # = ...  # type: int
            QsciLexerPython.Comment: '#808080',  # = ...  # type: int
            QsciLexerPython.Number: '#0000FF',  # = ...  # type: int
            QsciLexerPython.DoubleQuotedString: '#29994F',  # = ...  # type: int
            QsciLexerPython.SingleQuotedString: '#29994F',  # = ...  # type: int
            QsciLexerPython.Keyword: '#00008B',  # = ...  # type: int
            QsciLexerPython.TripleSingleQuotedString: '#29994F',  # = ...  # type: int
            QsciLexerPython.TripleDoubleQuotedString: '#29994F',  # = ...  # type: int
            QsciLexerPython.ClassName: '#060F89',  # = ...  # type: int
            QsciLexerPython.FunctionMethodName: '#060000',  # = ...  # type: int
            QsciLexerPython.Operator: '#D26F9D',  # = ...  # type: int
            QsciLexerPython.Identifier: 'black',  # = ...  # type: int
            QsciLexerPython.CommentBlock: '#808080',  # = ...  # type: int
            QsciLexerPython.UnclosedString: '#29994F',  # = ...  # type: int
            QsciLexerPython.HighlightedIdentifier: 'red',  # = ...  # type: int
            QsciLexerPython.Decorator: '#807F47',  # = ...  # type: int
            QsciLexerPython.DoubleQuotedFString: '#29994F',  # = ...  # type: int
            QsciLexerPython.SingleQuotedFString: '#29994F',  # = ...  # type: int
            QsciLexerPython.TripleSingleQuotedFString: '#29994F',  # = ...  # type: int
            QsciLexerPython.TripleDoubleQuotedFString: '#29994F',  # = ...  # type: int
            32: 'lightgray'  # 折叠线
        }
    }

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
