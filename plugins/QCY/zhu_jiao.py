from nonebot import on_command, CommandSession

__plugin_name__ = '助教'
__plugin_usage__ = r"""
助教相关工作

成绩    获取自己的成绩.
"""
@on_command('成绩查询', aliases=('成绩'))
async def 成绩查询(session: CommandSession):
    if session.event.detail_type == "private":
        await session.send(f'未实现的功能~')
    elif session.event.detail_type == "group":
        await session.send(f'为了用户隐私, 暂不在群聊中支持此功能')