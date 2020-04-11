from nonebot import on_notice, NoticeSession

神音群={80852074}

@on_notice('group_increase')
async def _(session: NoticeSession):
    # 发送欢迎消息
    if session.event.group_id in 神音群:
        await session.send('欢迎加入数学大家庭w')

@on_notice('group_decrease')
async def _(session: NoticeSession):
    # 发送退群消息
    if session.event.group_id in 神音群:
        await session.send(f'{session.event.user_id}小妹妹退群惹qwq')