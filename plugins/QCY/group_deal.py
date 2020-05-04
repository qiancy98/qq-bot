from nonebot import on_notice, NoticeSession
from config import 神音群ID

@on_notice('group_increase')
async def _(session: NoticeSession):
    # 发送欢迎消息
    if session.event.group_id in 神音群ID:
        await session.send('欢迎加入二次元抱抱群w')

@on_notice('group_decrease')
async def _(session: NoticeSession):
    # 发送退群消息
    if session.event.group_id in 神音群ID:
        await session.send(f'{session.event.user_id}小妹妹退群惹qwq')