from nonebot import on_command, CommandSession
from config import SUPERUSERS, SESSION_EXPIRE_TIMEOUT

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
        # 首先是否关闭
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
        # 然后输出状态
        elif cmd == "State[]":
            await session.send(f"Wolfram Play是否启动: {1 in kernel_on}")
        # 都不是, 那么运行结果
        else:
            if (1 not in kernel_on):
                kernel_on[1]=0
                mma_session.evaluate(wlexpr(f'kernel=LinkLaunch[First[$CommandLine] <> " -wstp -noicon"]'))
            if (supermode and session.event.user_id in SUPERUSERS):
                await session.send(mma2_run(cmd))
            else:
                out = mma_run(cmd)
                if (len(out)>=100):
                    pos = 100
                    await session.send(f"输出总长{len(out)}字符. 前100字符为:\n{out[:pos]}") #\n继续输出300字符请输入'y', 继续输出全部字符请输入'a', 从头全部输出请输入'A', 开启新的线程请等待{SESSION_EXPIRE_TIMEOUT}时间 或输入'n/N'. 只判断首字母.")
                    state_dict = {
                        'y': 300,
                        'a': 2000,
                        'A': -1,
                        'n': -2,
                        'N': -2,
                    }
                    # while (pos < len(out)):
                    #     state = session.get('state', prompt=f'(此功能目前有bug →) 请继续/重新输入, 或等待线程超时.')
                    #     if state[0] in state_dict:
                    #         state_code = state_code[state[0]]
                    #         if state_code == -2:
                    #             break
                    #         elif state_code == -1:
                    #             await session.send(out)
                    #             break
                    #         else:
                    #             await session.send(out[pos:pos+state_code])
                    #             pos += state_code
                else:
                    await session.send(out)
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
        session.pause('qwq 好像只有空白字符诶, 请重新输入?')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的命令），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg

def mma_run(cmd:str) -> str:
    mma_session.evaluate(wlexpr(f'''out="";
        LinkWrite[kernel,
            EnterTextPacket[
                MemoryConstrained[
                    TimeConstrained[Unevaluated[({cmd}) // InputForm],30,out=out<>"TLE(30s)"]
                ,268435456,out=out<>"MLE(256M)"]
            ]
        ];'''))
    time.sleep(5)
    return mma_session.evaluate(wlexpr(f'''
        TimeConstrained[
            While[LinkReadyQ@kernel,
                temp=LinkRead[kernel];
                Switch[temp,
                    _TextPacket,out=out<>ToString[temp[[1]]]<>"\n",
                    _ReturnTextPacket,out=out<>ToString[temp[[1]]]<>"\n",
                    _ReturnPacket,out=out<>ToString[temp[[1,1]]]<>"\n",
                    _OutputNamePacket,out=out<>ToString[temp[[1]]],
                    _InputNamePacket,,
                    _,out=out<>ToString[temp]<>"\n"
                ]
            ];
        ,10,out="";out=out<>"输出时超时(10s)"];
        out'''))

def mma2_run(cmd:str) -> str:
    return mma_session.evaluate(wlexpr(f'''
                MemoryConstrained[
                    TimeConstrained[({cmd}) // ToString,30,"TLE(30s)"]
                ,268435456,"MLE(256M)"]
                '''))