# from types import MethodType
#
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QIcon
# from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QFrame, QVBoxLayout, QPushButton, QToolButton, QMenu
#
# from pyqt5utils.components.styles import StylesHelper
# from pyqt5utils.components.widgets.dialogs import ShadowDialog
# from . import register, ToolBarActionMixIn, ToolBarTypes
# from ..factorys import add_styled, make_styled
# from ..styles import current_styles
#
# index = 5
# icon = ':/icon/fenxi.svg'
#
#
# @register('代码分析', index=index, icon=icon)
# class CodeAction(ToolBarActionMixIn):
#
#     def make_action(self, icon_path, tool_tip, parent) -> ToolBarTypes:
#         def render_custom_style(this):
#             background = current_styles.background_lighter
#             border = current_styles.border_lighter
#             foreground = current_styles.foreground
#             darker = current_styles.background_darker
#
#             this.setStyleSheet('color:%s;font-family:微软雅黑;background:transparent' % foreground)
#
#         print(icon_path, tool_tip, parent)
#         btn = QPushButton()
#         btn.setIcon(QIcon(icon_path))
#         btn.setText('代码分析')
#         btn.setToolTip(tool_tip)
#         # btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
#         # btn.setPopupMode(QToolButton.InstantPopup)
#         btn.render_custom_style = MethodType(render_custom_style, btn)
#
#         menu: QMenu = make_styled(QMenu, 'menu')
#         a1 = menu.addAction('错误检查')
#         a2 = menu.addAction('引用分析')
#         a3 = menu.addAction('代码跳转')
#         a4 = menu.addAction('悬浮提示')
#         a1.setCheckable(True)
#         a2.setCheckable(True)
#         a3.setCheckable(True)
#         a4.setCheckable(True)
#         btn.setMenu(menu)
#
#         add_styled(btn, 'custom-style')
#         return [
#             (None, None),
#             (btn, None)
#         ]
#
#     def action_slot(self):
#         def render_custom_style(this):
#             background = current_styles.background_lighter
#             border = current_styles.border_lighter
#             foreground = current_styles.foreground
#             darker = current_styles.background_darker
#             this.frame_less.setStyleSheet('#FrameLess{background:%s;color:%s;font-family:微软雅黑;border:1px solid %s}' % (background, foreground, border))
#             list_view.setStyleSheet('QListWidget{background:%s; color:%s;border:0px solid %s}' % (
#                 background, foreground, border
#             ))
#             StylesHelper.set_v_history_style_dynamic(list_view, color=current_styles.handler, background='transparent', width=10)
#             StylesHelper.set_h_history_style_dynamic(list_view, color=current_styles.handler, background='transparent', height=10)
#             label.setStyleSheet('QLabel{background:%s;padding:5px;color:%s;font-family:微软雅黑}' % (darker, foreground))
#
#         theme_shadow = ShadowDialog(shadow_color='transparent')
#         frame = QFrame()
#         frame.setFrameShape(QFrame.NoFrame)
#         fl = QVBoxLayout(frame)
#         fl.setContentsMargins(0, 0, 0, 0)
#         fl.setSpacing(0)
#
#         label = QLabel('主题')
#         label.setAlignment(Qt.AlignCenter)
#         fl.addWidget(label)
#
#         list_view = QListWidget()
#         list_view.itemClicked.connect(self._item_click)
#         list_view.itemDoubleClicked.connect(lambda item: self._change_theme(item, theme_shadow))
#
#         theme_list = current_styles.theme_list()
#         list_view.addItems(theme_list)
#         fl.addWidget(list_view)
#         theme_shadow.add_content(frame)
#
#         theme_shadow.render_custom_style = MethodType(render_custom_style, theme_shadow)
#         add_styled(theme_shadow, 'custom-style')
#
#         theme_shadow.center(self.app)
#
#     def _change_theme(self, item: QListWidgetItem, shadow):
#         theme = item.text()
#         current_styles.change(theme)
#         shadow.close()
#
#     def _item_click(self, item):
#         theme = item.text()
#         current_styles.change(theme)
