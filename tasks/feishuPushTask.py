from analyze.Summary import dailyReportToOne
from analyze.informTemplate import informText
from utils.QueueModule import msgpq
from conf import *
from utils.TaskManager import task_manager
from utils.databaseMG import searchUserName, searchUserThreadFromId, getUser, searchThread


def FeishuPushThread():
    while True:
        tk = msgpq.get()
        handler = task_manager.get_handler_with_task(tk)
        handler(tk)
        msgpq.task_done()

def cursor_to_text(cursor):
    # 遍历游标中的每个文档，将其转换为字符串并逐行拼接
    result = ""
    for document in cursor.limit(5):
        # 将每个文档转换为字符串，并添加换行符
        result += str(document) + "\n"

    return result
@task_manager.register('summary')
def summaryTask(tk):
    dailyReportToOne(tk.data['openid'])

@task_manager.register('searchUserName')
def searchUserNameTask(tk):
    informText(tk.data['openid'], cursor_to_text(searchUserName(tk.data['content'])))

@task_manager.register('searchUserId')
def searchUserIdTask(tk):
    informText(tk.data['openid'], getUser(tk.data['content']))

@task_manager.register('searchContentFromUserID')
def searchContentFromUserIDTask(tk):
    informText(tk.data['openid'], cursor_to_text(searchUserThreadFromId(tk.data['content'])))

@task_manager.register('searchContent')
def searchContentTask(tk):
    informText(tk.data['openid'], cursor_to_text(searchThread(tk.data['content'])))

@task_manager.register('error')
def errorTask(tk):
    for openid in informid:
        tag = tk.data['tag']
        message = tk.data['msg']
        informText(openid, f'错误信息提示{tag}:{message}')