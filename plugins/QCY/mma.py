from nonebot import on_command, CommandSession
from config import SUPERUSERS

from wolframclient.evaluation import WolframLanguageSession  # MMA
from wolframclient.language import wl, wlexpr  # MMA
import time

mma_session=WolframLanguageSession()

__plugin_name__ = 'Wolfram命令'
__plugin_usage__ = r"""
Wolfram命令

mma [command] 用wolfram语言计算 (仅限bot管理员) 时限30s, 空间256M
wolfram [command] 同上
"""

@on_command('mma2', aliases=[])
async def mma2(session: CommandSession):
    await mma(session,True)

@on_command('mma', aliases=['mathematica','Mathematica','wolfram'])
async def mma(session: CommandSession, supermode = False, kernel_on={}):
    # 获取设置了名称的插件列表
    if session.event.detail_type =='group' or session.event.user_id in SUPERUSERS:
        cmd = session.get('cmd', prompt='请输入命令?')
        if cmd == "Exit[]":
            if session.event.user_id not in SUPERUSERS:
                await session.send("错误: 权限不够, 无法关闭Wolfram Play.")
            elif (1 not in kernel_on):
                await session.send("错误: Wolfram Play已经是关闭状态.")
            else:
                mma_session.evaluate(wlexpr(f'LinkClose[kernel]'))
                mma_session.terminate()
                del kernel_on[1]
                await session.send("已成功关闭Wolfram Play.")
        elif cmd == "State[]":
            await session.send(f"Wolfram Play是否启动: {1 in kernel_on}")
        else:
            if (1 not in kernel_on):
                kernel_on[1]=0
                mma_session.evaluate(wlexpr(f'kernel=LinkLaunch[First[$CommandLine] <> " -wstp -noicon"]'))
            if (supermode and session.event.user_id in SUPERUSERS):
                await session.send(mma2_run(cmd))
            else:
                await session.send(mma_run(cmd))
    else:
        await session.send(f"错误: 权限不够, 无法使用mma.")

# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@mma2.args_parser
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

# def mma_run(cmd:str,this_user:int,users=dict()) -> str:
#     return "此功能暂时下线"

def mma_run(cmd:str) -> str:
    mma_session.evaluate(wlexpr(f'''out="";
        LinkWrite[kernel,
            EnterTextPacket[
                MemoryConstrained[
                    TimeConstrained[({cmd}) // ToString,30,out=out<>"TLE(30s)"]
                ,268435456,out=out<>"MLE(256M)"]
            ]
        ];'''))
    time.sleep(5)
    s=mma_session.evaluate(wlexpr(f'''
        TimeConstrained[
            While[LinkReadyQ@kernel,
                x=LinkRead[kernel];
                Switch[x,
                    _TextPacket,out=out<>ToString[x[[1]]]<>"\n",
                    _ReturnTextPacket,out=out<>ToString[x[[1]]]<>"\n",
                    _OutputNamePacket,out=out<>ToString[x[[1]]],
                    _InputNamePacket,,
                    _,out=out<>ToString[x]<>"\n"
                ]
            ];
        ,10,out="";out=out<>"输出时超时(10s)"];
        out'''))
    if (len(s)>=100):
        return "输出超过100字符. 前100字符为:\n" + s[:100]
    else:
        return s

def mma2_run(cmd:str) -> str:
    return mma_session.evaluate(wlexpr(f'''
                MemoryConstrained[
                    TimeConstrained[({cmd}) // ToString,30,"TLE(30s)"]
                ,268435456,"MLE(256M)"]
                '''))