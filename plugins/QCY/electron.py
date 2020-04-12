from nonebot import on_command, CommandSession
import random

__plugin_name__ = '水群'
__plugin_usage__ = r"""
水群

电    获得随机电疗时间! (仅限群聊)
"""

@on_command('电', aliases=('电疗','放电'))
async def 电(session: CommandSession):
    if session.event.detail_type == "private":
        await session.send(f'这里是私聊哦!')
    elif session.event.detail_type == "group":
        t = random.randint(1,3600)
        bot = session.bot
        await bot.set_group_ban(group_id=session.event.group_id,user_id=session.event.user_id,duration=t)
        await session.send(f'喵呜喵呜~ 这道闪电时长{t}秒哦w')