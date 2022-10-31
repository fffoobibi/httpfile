from . import register, ToolBarActionMixIn

index = 2
icon = ':/icon/shuaxin.svg'


@register('刷新', index=index, icon=icon)
class FreshAction(ToolBarActionMixIn):
    pass
