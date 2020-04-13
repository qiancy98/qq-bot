import nonebot
from nonebot import on_command, CommandSession
from config import SUPERUSERS
import time
import os

@on_command('latex', aliases=['LaTeX'])
async def latex(session: CommandSession):
    if session.event.user_id in SUPERUSERS:
        cmd = session.get('cmd', prompt='请输入命令?')
        latex_run(cmd)
        await session.send("Some Image here")
    else:
        await session.send(f"错误: 权限不够, 无法使用latex.")

# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@latex.args_parser
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

def latex_run(source: str)->str:
    pre = r"""
    \documentclass[convert]{standalone}

    % Basic Packages
    \usepackage{amsmath,amsthm,amsfonts,amssymb,mathtools}

    % Graph
    \usepackage{tikz}
    \usetikzlibrary{calc}
    \usetikzlibrary{positioning}

    % Other packages
    \usepackage{ifthen} % 支持条件判断
    \usepackage[scheme=plain]{ctex}

    \begin{document}
    $"""
    bak = r"""$
    \end{document}
    """
    tempfilename = "TEMP" + hex(hash(source) ^ time.time_ns())[1:]
    with open(f"{tempfilename}.tex", "w") as file:
        file.write(pre + source + bak)
    if r := os.system(f"xelatex -interaction=nonstopmode -quiet -shell-escape {tempfilename}.tex > {tempfilename}.mylog"):
        print(r)
        if r == 124 or r == 128+9 or r == 31744:
            time.sleep(15)
        with open(f"{tempfilename}.log", "r") as file:
            error = file.read()
        raise RuntimeError(error[error.find("\n!"):error.find("Here is how much of")])