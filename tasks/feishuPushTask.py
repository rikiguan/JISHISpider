from analyze.Summary import dailyReportToOne
from analyze.informTemplate import informText
from utils.QueueModule import msgpq
from conf import *

def FeishuPushThread():
    while True:
        tk = msgpq.get()
        if tk.task_type == 'summary':
            dailyReportToOne(tk.data['openid'])
        if tk.task_type == 'error':
            for openid in informid:
                tag=tk.data['tag']
                message=tk.data['msg']
                informText(openid,f'错误信息提示{tag}:{message}')
        msgpq.task_done()

