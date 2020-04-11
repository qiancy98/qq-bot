from nonebot import on_command, CommandSession
from config import SUPERUSERS

from wolframclient.evaluation import WolframLanguageSession  # MMA
from wolframclient.language import wl, wlexpr  # MMA
mma_session=WolframLanguageSession()

__plugin_name__ = 'Wolfram命令'
__plugin_usage__ = r"""
Wolfram命令

mma [command] 用wolfram语言计算 (仅限bot管理员)
wolfram [command] 同上
"""

@on_command('mma', aliases=['mathematica','Mathematica','wolfram'])
async def mma(session: CommandSession):
    # 获取设置了名称的插件列表
    if session.event.detail_type=='private' and session.event.user_id in SUPERUSERS:
        cmd = session.get('cmd', prompt='请输入命令?')
        cmd += ' // ToString'
        await session.send(mma_session.evaluate(wlexpr(cmd)))
    else:
        await session.send(f"错误: 权限不够, 您使用的账号是: {session.event.user_id}")

# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@mma.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将有效命令跟在命令名后面，作为参数传入
            session.state['cmd'] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的名称（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('qwq 没有找到mma命令诶, 请重新输入?')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的命令），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg

