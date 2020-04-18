from nonebot import on_command, CommandSession
import defusedxml
import xlrd

defusedxml.defuse_stdlib()

__plugin_name__ = '助教'
__plugin_usage__ = r"""
助教相关工作

成绩    获取自己的成绩. (仅支持本学期学生使用.)
"""

@on_command('成绩查询', aliases=('成绩'))
async def 成绩查询(session: CommandSession):
    if session.event.detail_type == "private":
        QQ_To_Name = {674880178:"唐国栋"}
        user_QQ = session.event.user_id
        if user_QQ not in QQ_To_Name:
            await session.finish("未查找到此人。请检查是否使用正确的QQ？")
            return
        else:
            user_name = QQ_To_Name[user_QQ]
        file_name = R"D:\Google 云端硬盘\2019-2024 直博\2019.1\16 数学助教\高等代数\作业概况\_高代平时成绩.xlsx"
        file = secure_open_workbook(filename=file_name)
        sheet_name = ["平时成绩","期中小测","期中考试","期末小测","期末考试"]
        sheet_comment = {"平时成绩":"注：W4,W10没有作业"}
        for _i in sheet_name:
            try:
                sheet = file.sheet_by_name(_i)
                row_title = sheet.row_values(0)
                R = sheet.ncols
                L = row_title.index("姓名")
                row_user = sheet.row_values(sheet.col_values(L).index(user_name))
                str_list = [sheet.name]
                for _j in range(L,R):
                    str_list.append(f"{row_title[_j]}\t{row_user[_j]}")
                if _i in sheet_comment:
                    str_list.append(sheet_comment[_i])
            except ValueError:
                await session.finish("qwq在表格[{_i}]的字符串匹配中出错：ValueError。请联系助教咨询？")
                raise
            except:
                await session.finish("qwq在表格[{_i}]的字符串匹配中出错：未知错误。请联系助教咨询？")
                raise
            else:
                str_send = '\n'.join(str_list)
                await session.send(str_send)
    elif session.event.detail_type == "group":
        await session.send(f'为了防止错发成绩到群内, 暂不在群聊中支持此功能')
    else:
        await session.send(f'未定义的地方。聊天环境类型：{session.event.detail_type}')

def secure_open_workbook(**kwargs):
    try:
        return xlrd.open_workbook(**kwargs)
    except defusedxml.common.EntitiesForbidden:
        raise ValueError('Please use a xlsx file without XEE')
