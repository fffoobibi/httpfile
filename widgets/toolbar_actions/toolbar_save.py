from . import register, ToolBarActionMixIn

index = 1
icon = ':/icon/baocun.svg'


@register('全部保存', index=index, icon=icon)
class SaveAction(ToolBarActionMixIn):
    pass