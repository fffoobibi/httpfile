# from enum import Enum
#
#
# class Sh(str, Enum):
#     chapter_list_style = '''
#         QListWidget::Item:hover:active{background-color: rgba(153, 149, 149, 80);color:#CCCCCC;border:none}
#         QListWidget::Item{color:#CCCCCC; border:none;margin-left:10px}
#         QListWidget::Item:selected{background-color: black;color: #CC295F}
#         QListWidget{outline:0px; background-color: transparent; border:none}
#     '''  # chapters_widget listwidget
#
#     vertical_scroll_style = '''
#         QScrollBar:vertical {background: black; padding: 0px;border-radius: 3px; max-width: 12px;}
#         QScrollBar::handle:vertical {background: rgba(153, 149, 149, 80);min-height: 20px;border-radius: 3px;}
#         QScrollBar::add-page:vertical {background: none;}
#         QScrollBar::sub-page:vertical {background: none;}
#         QScrollBar::add-line:vertical { background: none;}
#         QScrollBar::sub-line:vertical {background: none; }
#     '''  # more_widget scrollarea
#
#     hori_scroll_style = '''
#         QScrollBar:horizontal {background: black; padding: 0px;border-radius: 3px; max-width: 12px;}
#         QScrollBar::handle:horizontal {background: rgba(153, 149, 149, 80);min-height: 20px;border-radius: 3px;}
#         QScrollBar::add-page:horizontal {background: none;}
#         QScrollBar::sub-page:horizontal {background: none;}
#         QScrollBar::add-line:horizontal { background: none;}
#         QScrollBar::sub-line:horizontal {background: none; }
#     '''  # more_widget scrollarea
#
#     upload_scroll_style = '''
#         QScrollBar:horizontal {background: #E4E4E4;padding: 0px;border-radius: 3px;max-height: 5px;}
#         QScrollBar::handle:horizontal {background: gray;min-width: 20px;border-radius: 3px;}
#         QScrollBar::handle:horizontal:hover {background: #426BDD;}
#         QScrollBar::handle:horizontal:pressed {background: #426BDD;}
#         QScrollBar::add-page:horizontal {background: none;}
#         QScrollBar::sub-page:horizontal {background: none;}
#         QScrollBar::add-line:horizontal {background: none;}
#         QScrollBar::sub-line:horizontal {background: none;}
#        '''  # more_widget scrollarea
#
#     pic_dialog_list_style = '''
#             QListWidget::Item:hover:active{background-color: transparent; color:#CCCCCC;border:none}
#             QListWidget::Item{color:#CCCCCC;border:none}
#             QListWidget::Item:selected{ background-color: black;color: #CC295F}
#             QListWidget{outline:0px; background-color: transparent; border:none}
#         '''  # more_widget latest_dialog listwidget
#
#     pic_dialog_style = '''
#         QDialog{border:1px solid gray}QLabel{color:white; font-family: 微软雅黑}QPushButton{color:white;font-family: 微软雅黑}
#         '''  # more_widget latest_dialog
#
#     table_v_scroll_style = '''
#         QScrollBar:vertical {background: #282A36;padding: 0px; border-radius: 3px;max-width: 8px;}
#         QScrollBar::handle:vertical {background: #54555D; min-height: 20px; border-radius: 3px;}
#         QScrollBar::handle:vertical:hover {background: #54555D;}
#         QScrollBar::handle:vertical:pressed {background: #54555D;}
#         QScrollBar::add-page:vertical { background: none;}
#         QScrollBar::sub-page:vertical {background: none;}
#         QScrollBar::add-line:vertical {background: none;}
#         QScrollBar::sub-line:vertical {background: none;}
#     '''
#
#     table_h_scroll_style = '''
#         QScrollBar:horizontal {background: #282A36;padding: 0px;border-radius: 3px;max-height: 8px;}
#         QScrollBar::handle:horizontal {background: #54555D;min-width: 20px;border-radius: 3px;}
#         QScrollBar::handle:horizontal:hover {background: #54555D;}
#         QScrollBar::handle:horizontal:pressed {background: #54555D;}
#         QScrollBar::add-page:horizontal {background: none;}
#         QScrollBar::sub-page:horizontal {background: none;}
#         QScrollBar::add-line:horizontal {background: none;}
#         QScrollBar::sub-line:horizontal {background: none;}'''
#
#     historycombobox_listview_style = '''
#         QListView {outline: 0px;color: black;}
#         QListView::item:hover {color: white;background-color: #5F89DF;}
#         QListView::item{color: black;background-color: white;}'''
#
#     historycombobox_style = '''
#         QComboBox {font-family: "Microsoft YaHei";color: #000000;font-weight: bold;padding-left: 1px;border: 1px solid lightgray;border-radius:5px}
#         QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;}
#         QComboBox::down-arrow{width:  30px;height: 30px;image: url(':/imgs/下拉箭头小.svg')}'''
#
#     site_button_listview_style = '''
#         QListView::item:hover{background: white;color:black;}
#         QListView::item{border-bottom:1px solid rgb(212, 212, 212)}
#         QListView{outline:0px;background: transparent;border:1px solid lightgray}'''
#
#
#     dynamic_menu_style = '''
#             QMenu {background-color : %s;padding:5px;border:1px solid %s}
#             QMenu::item {font-size:9pt;background-color: %s;color: %s;padding: 10px 3px 8px 3px;margin: 3px 3px;}
#             QMenu::item:selected { background-color : red;}
#             QMenu::icon:checked {background: rgb(253,253,254); position: absolute;top: 1px;right: 1px;bottom: 1px;left: 1px;}
#             QMenu::separator {height: 2px;background: rgb(235,235,236);margin-left: 10px;margin-right: 10px;}'''
#
#     submit_list_style = '''
#         QListWidget::Item:hover{background-color:transparent;color:black}
#         QListWidget::Item{/*border-bottom:1px solid rgb(212, 212, 212)*/}
#         QListWidget::Item:selected{background-color: transparent;color:black;border-radius:5px}
#         QListWidget{outline:0px; background-color: transparent;border-top:1px solid lightgray;border-bottom:1px solid lightgray;
#             border-left:0px solid lightgray;border-right:0px solid lightgray;}'''
#
#     green_v_scroll_style = '''
#         QScrollBar:vertical {background: #E4E4E4;padding: 0px;border-radius: 3px;max-width: 12px;}
#         QScrollBar::handle:vertical {background: lightgray;min-height: 20px;border-radius: 3px;}
#         QScrollBar::handle:vertical:hover {background: #00BB9E;}
#         QScrollBar::handle:vertical:pressed {background: #00BB9E;}
#         QScrollBar::add-page:vertical {background: none;}
#         QScrollBar::sub-page:vertical {background: none;}
#         QScrollBar::add-line:vertical {background: none;}
#         QScrollBar::sub-line:vertical {background: none;}'''
#
#     list_page_style = '''
#         QListWidget::Item:hover{background-color: #E9E9E9; color:black; border:none;border-bottom:1px solid rgb(212, 212, 212)}
#         QListWidget::Item{border-bottom:1px solid rgb(212, 212, 212);border:none;color: lightgray}
#         QListWidget{outline:0px; background-color: transparent;border:none}
#         '''
#
#     upload_list_page_style = '''
#             QListWidget::Item:hover{background-color: transparent; color:black; border:none}
#             QListWidget::Item{border: none;background-color: transparent;}
#             QListWidget{outline:0px; background-color: transparent;border:none}
#         '''
#
#     history_list_page_style = '''
#             QListWidget::Item:hover{background-color: lightgray; color:transparent; border:none}
#             QListWidget::Item{border:1px solid white;background-color: white; border-radius:5px;color:transparent}
#             QListWidget{outline:0px; background-color: transparent;border:none}
#             '''
#
#     icon_page_style = '''
#         QListWidget::Item:hover{background-color:transparent; color:black}
#         QListWidget::Item{border: none}
#         QListWidget{outline:0px; background-color: transparent;border:none}'''
#
#     fileter_listview_style = '''
#         QListView::item:hover{background: white;color:black;border:none}
#         QListView::item{border-bottom:1px solid rgb(212, 212, 212)}
#         QListView::item:selected{background: lightgray;color:black}
#         QListView{outline:0px;background: transparent;border:none}'''
#
#     header_view_style = """
#         QHeaderView::section
#         {
#             border-right: 0px solid white;
#             border-left:0px solid white;
#             border-top:none;
#             border-bottom: none;
#             background-color:#383A46;
#         }
#          QHeaderView
#         {   color:white;
#             font-family: 微软雅黑;
#             border-right: 0px solid white;
#             border-left: 0px solid white;
#             border-top: none;
#             border-bottom: none;
#             background-color:#383A46;
#             font-weight: bold
#         }
#     """
#
#     header_view_style2 = """
#         QHeaderView::section
#         {
#             text-align: left;
#             border-right: 0px solid white;
#             border-left:0px solid white;
#             border-top:none;
#             border-bottom: none;
#             background-color:transparent;
#         }
#          QHeaderView
#         {
#             border-right: 0px solid white;
#             border-left: 0px solid white;
#             border-top: none;
#             border-bottom: none;
#             background-color:transparent;
#         }
#     """
#
#     header_view_style3 = """
#         QHeaderView::section
#         {
#             text-align: left;
#             border-right: 0px solid white;
#             border-left:0px solid white;
#             border-top:none;
#             border-bottom: none;
#             background-color:transparent;
#         }
#          QHeaderView
#         {
#             border-right: 0px solid white;
#             border-left: 0px solid lightgray;
#             border-top: none;
#             border-bottom: 0px solid lightgray;
#             background-color:transparent;
#         }
#     """
#
#     header_view_style4 = """
#         QHeaderView::section
#         {
#         border:none
#         }
#          QHeaderView
#         {
#             border:none;
#             font-size: 10pt;
#             font-weight: bold
#         }
#     """
#
#     number_line_ok = """
#     QLineEdit{border:2px solid #ADC3F4;
#             border-radius: 3px;
#             font-family: 微软雅黑;
#             height:26px}
#     QLineEdit:focus{
#             border:2px solid rgb(122,161,245);
#             }
#     """
#
#     number_line_fail = """
#          QLineEdit{border:2px solid red;
#                         border-radius: 3px;
#                         font-family: 微软雅黑;
#                         height:26px}
#          QLineEdit:focus{
#                         border:2px solid rgb(122,161,245);
#                         }
#     """
#
#     bank_line_ok = """
#         QComboBox {
#                 border:2px solid #ADC3F4;
#                 border-radius: 3px;
#                 height:26px;
#                 padding-left: 1px;}
#         QComboBox:focus{
#             border: 2px solid rgb(122,161,245)}
#         QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
#                 }
#         QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/箭头 下(1).svg')}
#         QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}
#     """
#
#     bank_line_fail = """
#         QComboBox {
#             border:2px solid red;
#             border-radius: 3px;
#             height:26px;
#             padding-left: 1px;}
#         QComboBox:focus{
#             border: 2px solid rgb(122,161,245)}
#         QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
#             }
#         QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/箭头 下(1).svg')}
#         QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}
#                 """
#


from enum import Enum

from PyQt5.QtWidgets import QListView, QWidget


class Sh(str, Enum):
    chapter_list_style = ''' 
        QListWidget::Item:hover:active{background-color: rgba(153, 149, 149, 80);color:#CCCCCC;border:none}
        QListWidget::Item{color:#CCCCCC; border:none;margin-left:10px}
        QListWidget::Item:selected{background-color: black;color: #CC295F}
        QListWidget{outline:0px; background-color: transparent; border:none}
    '''  # chapters_widget listwidget

    vertical_scroll_style = '''
        QScrollBar:vertical {background: black; padding: 0px;border-radius: 3px; max-width: 12px;}
        QScrollBar::handle:vertical {background: rgba(153, 149, 149, 80);min-height: 20px;border-radius: 3px;}        
        QScrollBar::add-page:vertical {background: none;height:0px}
        QScrollBar::sub-page:vertical {background: none;height:0px}
        QScrollBar::add-line:vertical {background: none;height:0px}
        QScrollBar::sub-line:vertical {background: none;height:0px}
        QScrollBar::down-arrow:vertical{height:0px}
        QScrollBar::up-arrow:vertical{height:0px}
    '''  # more_widget scrollarea

    hori_scroll_style = '''
        QScrollBar:horizontal {background: black; padding: 0px;border-radius: 3px; max-width: 12px;}
        QScrollBar::handle:horizontal {background: rgba(153, 149, 149, 80);min-height: 20px;border-radius: 3px;}
        QScrollBar::add-page:horizontal {background: none;width:0px}
        QScrollBar::sub-page:horizontal {background: none;width:0px}
        QScrollBar::add-line:horizontal {background: none; width:0px}
        QScrollBar::sub-line:horizontal {background: none;width:0px}
        QScrollBar::down-arrow:horizontal{background: none; width:0px}
        QScrollBar::up-arrow:horizontal{background: none; width:0px}
    '''  # more_widget scrollarea

    upload_scroll_style = '''
        QScrollBar:horizontal {background: #E4E4E4;padding: 0px;border-radius: 3px;max-height: 5px;}
        QScrollBar::handle:horizontal {background: gray;min-width: 20px;border-radius: 3px;}
        QScrollBar::handle:horizontal:hover {background: #426BDD;}
        QScrollBar::handle:horizontal:pressed {background: #426BDD;}
        QScrollBar::add-page:horizontal {background: none;width:0px}
        QScrollBar::sub-page:horizontal {background: none;width:0px}
        QScrollBar::add-line:horizontal {background: none; width:0px}
        QScrollBar::sub-line:horizontal {background: none;width:0px}
        QScrollBar::down-arrow:horizontal{background: none; width:0px}
        QScrollBar::up-arrow:horizontal{background: none; width:0px}
       '''  # more_widget scrollarea

    pic_dialog_list_style = '''
            QListWidget::Item:hover:active{background-color: transparent; color:#CCCCCC;border:none}
            QListWidget::Item{color:#CCCCCC;border:none}
            QListWidget::Item:selected{ background-color: black;color: #CC295F}
            QListWidget{outline:0px; background-color: transparent; border:none}
        '''  # more_widget latest_dialog listwidget

    pic_dialog_style = '''
        QDialog{border:1px solid gray}QLabel{color:white; font-family: 微软雅黑}QPushButton{color:white;font-family: 微软雅黑}
        '''  # more_widget latest_dialog

    history_v_scroll_style = '''
        QScrollBar:vertical {background: #E4E4E4;padding: 0px; border-radius: 3px;max-width: 8px;}
        QScrollBar::handle:vertical {background: #416CDD; min-height: 20px; border-radius: 3px;}
        QScrollBar::handle:vertical:hover {background: #0945DE;}
        QScrollBar::handle:vertical:pressed {background: #0945DE;}
        QScrollBar::add-page:vertical {background: none;height:0px}
        QScrollBar::sub-page:vertical {background: none;height:0px}
        QScrollBar::add-line:vertical {background: none;height:0px}
        QScrollBar::sub-line:vertical {background: none;height:0px}
        QScrollBar::down-arrow:vertical{height:0px}
        QScrollBar::up-arrow:vertical{height:0px}
    '''

    history_v_scroll_style_dynamic = '''
        QScrollBar:vertical {background: %s;padding: 0px; border-radius: 0px;max-width: %spx;}
        QScrollBar::handle:vertical {background: %s; min-height: 20px; border-radius: 0px;}
        QScrollBar::handle:vertical:hover {background: %s;}
        QScrollBar::handle:vertical:pressed {background: %s;}
        QScrollBar::add-page:vertical {background: none;height:0px}
        QScrollBar::sub-page:vertical {background: none;height:0px}
        QScrollBar::add-line:vertical {background: none;height:0px}
        QScrollBar::sub-line:vertical {background: none;height:0px}
        QScrollBar::down-arrow:vertical{height:0px}
        QScrollBar::up-arrow:vertical{height:0px}
    '''

    history_h_scroll_style_dynamic = '''
        QScrollBar:horizontal {background: %s;padding: 0px; border-radius: 0px; max-height: %spx;}
        QScrollBar::handle:horizontal {background: %s; min-width: 20px; border-radius: 0px;}
        QScrollBar::handle:horizontal:hover {background: %s;}
        QScrollBar::handle:horizontal:pressed {background: %s;}
        QScrollBar::add-page:horizontal {background: none;height:0px}
        QScrollBar::sub-page:horizontal {background: none;height:0px}
        QScrollBar::add-line:horizontal {background: none;height:0px}
        QScrollBar::sub-line:horizontal {background: none;height:0px}
        QScrollBar::down-arrow:horizontal{height:0px}
        QScrollBar::up-arrow:horizontal{height:0px}
    '''

    history_v_gray_scroll_style = '''
            QScrollBar:vertical {background: #E4E4E4;padding: 0px; border-radius: 2px;max-width: 5px;}
            QScrollBar::handle:vertical {background: #416CDD; min-height: 20px; border-radius: 2px;}
            QScrollBar::handle:vertical:hover {background: #0945DE;}
            QScrollBar::handle:vertical:pressed {background: #0945DE;}
            QScrollBar::add-page:vertical {background: none;height:0px}
            QScrollBar::sub-page:vertical {background: none;height:0px}
            QScrollBar::add-line:vertical {background: none;height:0px}
            QScrollBar::sub-line:vertical {background: none;height:0px}
            QScrollBar::down-arrow:vertical{height:0px}
            QScrollBar::up-arrow:vertical{height:0px}
    '''

    history_h_scroll_style = '''
        QScrollBar:horizontal {background: #E4E4E4;padding: 0px; border-radius: 3px;max-height: 8px;}
        QScrollBar::handle:horizontal {background: #416CDD; min-height: 20px; border-radius: 3px;}
        QScrollBar::handle:horizontal:hover {background: #0945DE;}
        QScrollBar::handle:horizontal:pressed {background: #0945DE;}
        QScrollBar::add-page:horizontal {background: none;width:0px}
        QScrollBar::sub-page:horizontal {background: none;width:0px}
        QScrollBar::add-line:horizontal {background: none; width:0px}
        QScrollBar::sub-line:horizontal {background: none;width:0px}
        QScrollBar::down-arrow:horizontal{background: none; width:0px}
        QScrollBar::up-arrow:horizontal{background: none; width:0px}
    '''

    debugtextedit_v_scroll_style = '''
        QScrollBar:vertical {background: #E4E4E4;padding: 0px; border-radius: 3px;max-width: 12px;}
        QScrollBar::handle:vertical {background: gray; min-height: 20px; border-radius: 3px;}
        QScrollBar::handle:vertical:hover {background: #00BB9E;}
        QScrollBar::handle:vertical:pressed {background: #00BB9E;}
        QScrollBar::add-page:vertical {background: none;height:0px}
        QScrollBar::sub-page:vertical {background: none;height:0px}
        QScrollBar::add-line:vertical {background: none;height:0px}
        QScrollBar::sub-line:vertical {background: none;height:0px}
        QScrollBar::down-arrow:vertical{height:0px}
        QScrollBar::up-arrow:vertical{height:0px}
        '''

    debugtextedit_h_scroll_style = '''
        QScrollBar:horizontal {background: #E4E4E4;padding: 0px;border-radius: 3px;max-height: 8px;}
        QScrollBar::handle:horizontal {background: gray;min-width: 20px;border-radius: 3px;}
        QScrollBar::handle:horizontal:hover {background: #426BDD;}
        QScrollBar::handle:horizontal:pressed {background: #426BDD;}
        QScrollBar::add-page:horizontal {background: none;width:0px}
        QScrollBar::sub-page:horizontal {background: none;width:0px}
        QScrollBar::add-line:horizontal {background: none; width:0px}
        QScrollBar::sub-line:horizontal {background: none;width:0px}
        QScrollBar::down-arrow:horizontal{background: none; width:0px}
        QScrollBar::up-arrow:horizontal{background: none; width:0px}'''

    historycombobox_listview_style = '''
        QListView {outline: 0px;color: black;}
        QListView::item:hover {color: white;background-color: #5F89DF;}
        QListView::item{color: black;background-color: white; height:25px}'''

    historycombobox_listwidget_style = '''
            QListWidget {outline: 0px;color: black;}
            QListWidget::item:hover {color: white;background-color: #5F89DF;}
            QListWidget::item{color: black;background-color: white; height:25px}'''

    historycombobox_style = '''
        QComboBox {font-family: "Microsoft YaHei";color: #000000;font-weight: bold;padding-left: 1px;border: 1px solid lightgray;border-radius:5px}
        QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;}
        QComboBox::down-arrow{width:  30px;height: 30px;image: url(':/imgs/下拉箭头小.svg')}'''

    site_button_listview_style = '''
        QListView::item:hover{background: white;color:black;}
        QListView::item{border-bottom:1px solid rgb(212, 212, 212)}
        QListView{outline:0px;background: transparent;border:1px solid lightgray}'''

    dynamic_menu_style = '''
            QMenu {background-color : %s;padding:5px;border:1px solid %s}
            QMenu::item {font-size:9pt;background-color: %s;color: %s;padding: 10px 3px 8px 3px;margin: 3px 3px;}
            QMenu::item:selected { background-color : red;}
            QMenu::icon:checked {background: rgb(253,253,254); position: absolute;top: 1px;right: 1px;bottom: 1px;left: 1px;}
            QMenu::separator {height: 2px;background: rgb(235,235,236);margin-left: 10px;margin-right: 10px;}'''

    submit_list_style = '''
        QListWidget::Item:hover{background-color:transparent;color:black}
        QListWidget::Item{/*border-bottom:1px solid rgb(212, 212, 212)*/}
        QListWidget::Item:selected{background-color: transparent;color:black;border-radius:5px}
        QListWidget{outline:0px; background-color: transparent;border-top:1px solid lightgray;border-bottom:1px solid lightgray;
            border-left:0px solid lightgray;border-right:0px solid lightgray;}'''

    green_v_scroll_style = '''
        QScrollBar:vertical {background: #E4E4E4;padding: 0px;border-radius: 3px;max-width: 12px;}
        QScrollBar::handle:vertical {background: lightgray;min-height: 20px;border-radius: 3px;}
        QScrollBar::handle:vertical:hover {background: #00BB9E;}
        QScrollBar::handle:vertical:pressed {background: #00BB9E;}
        QScrollBar::add-page:vertical {background: none;height:0px}
        QScrollBar::sub-page:vertical {background: none;height:0px}
        QScrollBar::add-line:vertical {background: none;height:0px}
        QScrollBar::sub-line:vertical {background: none;height:0px}
        QScrollBar::down-arrow:vertical{height:0px}
        QScrollBar::up-arrow:vertical{height:0px}
    '''

    list_page_style = '''
        QListWidget::Item:hover{background-color: #E9E9E9; color:black; border:none;border-bottom:1px solid rgb(212, 212, 212)}
        QListWidget::Item{border-bottom:1px solid rgb(212, 212, 212);border:none;color: lightgray}
        QListWidget{outline:0px; background-color: transparent;border:none}
        '''

    upload_list_page_style = '''
            QListWidget::Item:hover{background-color: transparent; color:black; border:none}
            QListWidget::Item{border: none;background-color: transparent;}
            QListWidget{outline:0px; background-color: transparent;border:none}
        '''

    history_list_page_style = '''
            QListWidget::Item:hover{background-color: lightgray; color:transparent; border:none}
            QListWidget::Item{border:1px solid white;background-color: white; border-radius:5px;color:transparent}
            QListWidget{outline:0px; background-color: transparent;border:none}
            '''

    history_list_page_style_with_select = '''
                QListWidget::Item:selected{background-color: lightgray; color:transparent; border:none}
                QListWidget::Item:hover{background-color: lightgray; color:transparent; border:none}
                QListWidget::Item{border:1px solid white;background-color: white; border-radius:5px;color:transparent}
                QListWidget{outline:0px; background-color: transparent;border:none}
                '''

    icon_page_style = '''
        QListWidget::Item:hover{background-color:transparent; color:black}
        QListWidget::Item{border: none}
        QListWidget{outline:0px; background-color: transparent;border:none}'''

    fileter_listview_style = '''
        QListView::item:hover{background: white;color:black;border:none}
        QListView::item{border-bottom:1px solid rgb(212, 212, 212)}
        QListView::item:selected{background: lightgray;color:black}
        QListView{outline:0px;background: transparent;border:none}'''

    header_view_style = """
        QHeaderView::section           
        {        
            border-right: 0px solid white;
            border-left:0px solid white;  
            border-top:none;
            border-bottom: none;    
            background-color:transparent;                
        }
         QHeaderView           
        {        
            border-right: 0px solid white;
            border-left: 0px solid white;  
            border-top: none;
            border-bottom: none;    
            background-color:transparent;     
            font-weight: bold              
        }
    """

    header_view_style2 = """
        QHeaderView::section           
        {        
            text-align: left;
            border-right: 0px solid white;
            border-left:0px solid white;  
            border-top:none;
            border-bottom: none;    
            background-color:transparent;                
        }
         QHeaderView           
        {        
            border-right: 0px solid white;
            border-left: 0px solid white;  
            border-top: none;
            border-bottom: none;    
            background-color:transparent;                
        }
    """

    header_view_style3 = """
        QHeaderView::section           
        {        
            text-align: left;
            border-right: 0px solid white;
            border-left:0px solid white;  
            border-top:none;
            border-bottom: none;    
            background-color:transparent;                
        }
         QHeaderView           
        {        
            border-right: 0px solid white;
            border-left: 0px solid lightgray;  
            border-top: none;
            border-bottom: 0px solid lightgray;    
            background-color:transparent;                
        }
    """

    header_view_style4 = """
        QHeaderView::section           
        {  
        border:none               
        }
         QHeaderView           
        {        
            border:none;
            font-size: 10pt;
            font-weight: bold              
        }
    """

    number_line_ok = """
        QLineEdit{border:2px solid #ADC3F4;
                border-radius: 3px;
                font-family: 微软雅黑;
                height:26px}
        QLineEdit:focus{
                border:2px solid rgb(122,161,245);
                }"""

    number_line_fail = """
         QLineEdit{border:2px solid red;
                        border-radius: 3px;
                        font-family: 微软雅黑;
                        height:26px}
         QLineEdit:focus{
                        border:2px solid rgb(122,161,245);
                        }"""

    bank_line_ok = """
        QComboBox {
                border:2px solid #ADC3F4;
                border-radius: 3px;
                height:26px;
                padding-left: 1px;}
        QComboBox:focus{
            border: 2px solid rgb(122,161,245)}
        QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
                }
        QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/箭头 下(1).svg')}
        QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}"""

    bank_line_fail = """
        QComboBox {
            border:2px solid red;
            border-radius: 3px;
            height:26px;
            padding-left: 1px;}
        QComboBox:focus{
            border: 2px solid rgb(122,161,245)}
        QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
            }
        QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/箭头 下(1).svg')}
        QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}"""

    StyleSheet = """
        /*标题栏*/
        /*最小化最大化关闭按钮通用默认背景*/
        #buttonMinimum,#buttonMaximum,#buttonClose {
            border: none;
            background-color:transparent

        }
        /*悬停*/
        #buttonMinimum:hover,#buttonMaximum:hover {
            color: white;
        }
        #buttonClose:hover {
            color: white;
        }
        /*鼠标按下不放*/
        #buttonMinimum:pressed,#buttonMaximum:pressed {
            background-color: Firebrick;
        }
        #buttonClose:pressed {
            color: white;
            background-color: Firebrick;
        }
    """

    menu_style = '''
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
        }
        QMenu::item:disabled{
            /*background-color:lightgray;*/
            color:lightgray;
        }
        QMenu::item:selected:disabled{
          background-color:transparent;
        }
    '''

    list_style_dynamic = '''
        QListWidget::item{border:0px solid lightgray; background-color: transparent; border-radius:0px;color:%s;border-bottom:1px solid gray}
        QListWidget::item:selected{background-color: transparent; color:%s; border:none;border-bottom:1px solid gray}
        QListWidget::item:hover{background-color: lightgray; color:%s; border:none;border-bottom:1px solid gray}
        QListWidget{outline:0px; background-color:%s ; border:1px solid %s; border-radius:%spx}
    '''


class Themes:
    theme_color = '#426BDD'
    hover_color = '#6D8BDE'

    button_color = '#426BDD'

    scroll_background_color = '#E4E4E4'
    handle_color = '#426BDD'
    handle_hover_color = '#6D8BDE'

    text_color = "black"

    card_color = 'white'

    _v_scroll_pattern = """
            QScrollBar:vertical {background: %s;padding: 0px; border-radius: 3px;max-width: %spx;}
            QScrollBar::handle:vertical {background: %s; min-height: 20px; border-radius: 3px;}
            QScrollBar::handle:vertical:hover {background: %s;}
            QScrollBar::handle:vertical:pressed {background: %s;}
            QScrollBar::add-page:vertical {background: none;height:0px}
            QScrollBar::sub-page:vertical {background: none;height:0px}
            QScrollBar::add-line:vertical {background: none;height:0px}
            QScrollBar::sub-line:vertical {background: none;height:0px}
            QScrollBar::down-arrow:vertical{height:0px}
            QScrollBar::up-arrow:vertical{height:0px}"""

    def list_style(self) -> str:
        pass

    def v_scroll_bar_style(self, handle_color: str = None, handle_hover_color: str = None,
                           scroll_background_color: str = None,
                           handle_width: int = None, handle_radius=None) -> str:
        return self._v_scroll_pattern % (
            scroll_background_color or self.scroll_background_color,
            handle_width or 10,
        )

    def h_scroll_bar_style(self) -> str:
        pass


class StylesHelper(object):
    @classmethod
    def set_v_history_style(cls, *target: QListView, color: str = None, width: int = None):
        for t in target:
            t.verticalScrollBar().setStyleSheet(Sh.history_v_scroll_style)

    @classmethod
    def set_h_history_style(cls, *target: QListView, color: str = None, width: int = None):
        for t in target:
            t.horizontalScrollBar().setStyleSheet(Sh.history_h_scroll_style)

    @classmethod
    def set_v_history_style_dynamic(cls, *target, color: str, background: str, width: int = 8):
        for t in target:
            t.verticalScrollBar().setStyleSheet(
                Sh.history_v_scroll_style_dynamic % (background, width, color, color, color))

    @classmethod
    def set_h_history_style_dynamic(cls, *target: QListView, color: str, background: str, height: int = 8):
        for t in target:
            t.horizontalScrollBar().setStyleSheet(
                Sh.history_h_scroll_style_dynamic % (background, height, color, color, color))

    @classmethod
    def set_list_view_style(cls, *target: QListView, background='transparent', text_color='transparent',
                            border_radius: int = 0, list_border='transparent', item_height: int = None):
        """
        QListWidget::item{border:0px solid lightgray; background-color: transparent; border-radius:5px;color:%s}
        QListWidget::item:selected{background-color: transparent; color:%s; border:none}
        QListWidget::item:hover{background-color: lightgray; color:%s; border:none}
        QListWidget{outline:0px; background-color:%s ; border:1px solid %s; border-radius:%spx}
        """
        for t in target:
            if item_height:
                styles = """
                QListWidget::item{border:0px solid lightgray; background-color: transparent; border-radius:0px; color:%s;height: %spx;
                border-bottom:1px solid gray
                }
                QListWidget::item:selected{background-color: transparent; color:%s; border:none; border-bottom:1px solid gray}
                QListWidget::item:hover{background-color: lightgray; color:%s; border:none; border-bottom:1px solid gray}
                QListWidget{outline:0px; background-color:%s ; border:1px solid %s; border-radius:%spx;border-bottom:1px solid gray}
                """
                print(styles % (
                    text_color, item_height, text_color, text_color,
                    background, list_border, border_radius,))
                t.setStyleSheet(styles % (
                    text_color, item_height, text_color, text_color,
                    background, list_border, border_radius,))
            else:
                t.setStyleSheet(Sh.list_style_dynamic % (
                    text_color, text_color, text_color,
                    background, list_border, border_radius))

    @classmethod
    def add_menu_style(cls, target: QWidget):
        style_sheet = target.styleSheet()
        style_sheet += '''
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
        }
        '''
        target.setStyleSheet(style_sheet)
