import json
import threading
import JiShiRequest
from analyze.Summary import dailyReportToAll, dailyReportToOne
from conf import *
from utils.useLog import log_thread
import time
from feishu import server
from tasks import timingTask
from utils.QueueModule import msgpq,pq
from utils.QueueModule import  Task
from utils.databaseES import es, getLastPostFromES, addToDatabaseFromList
from utils.logger import logger





def NewPostProducer():
    while True:
        res = getLastPostFromES()
        pq.put(Task(2, "newPost", {'from_id': res['_id'], 'from_time': res['_source']['p_time']}))
        time.sleep(30*60)


def handleNewPostTask(rq, tk, tag):
    response = rq.requestGetNewPostNum(tk.data['from_id'], tk.data['from_time'])
    if response.status_code != 200:
        return False

    data = json.loads(response.text)
    if data['errno'] != 0:
        return False

    num = data['data']['count']
    if(num ==0 ):
        return True

    response1 = rq.requestGetNewPost(tk.data['from_id'], tk.data['from_time'])
    if response1.status_code != 200:
        return False

    data1 = json.loads(response1.text)
    if data1['errno'] != 0 or len(data1['data']['list']) == 0:
        return False

    list1 = data1['data']['list']
    addToDatabaseFromList(tag, list1)
    if (int(num) == len(list1)):
        return True
    timestamp = list1[-1]['p_time']
    getnum = len(list1)

    while getnum < 2 * int(num) and int(timestamp) > int(tk.data['from_time']):
        response2 = rq.requestMainPageFromTime(timestamp)
        if response2.status_code != 200:
            return False
        data2 = json.loads(response2.text)
        if data2['errno'] != 0 or len(data2['data']['list']) == 0:
            return False
        list2 = data2['data']['list']
        addToDatabaseFromList(tag, list2)
        timestamp = list2[-1]['p_time']
        getnum += len(list2)
        time.sleep(5)
    return True

@log_thread()
def taskHandler(tag,rq,tk):
    if tk.task_type == 'newPost':
        return handleNewPostTask(rq, tk, tag)
    elif tk.task_type == 'type2':
        pass
    return False

def SpiderThread(token):
    tag = token[:5]
    rq = JiShiRequest.JiShi(token)
    while True:
        tk = pq.get()
        logger.info(f'任务获取{tk}')
        if not taskHandler(tag,rq,tk):
            logger.error(f'任务执行失败,任务为{tk}')
            tk.priority=1
            pq.put(tk)
        pq.task_done()


def FeishuPushThread():
    while True:
        tk = msgpq.get()
        if tk.task_type == 'summary':
            dailyReportToOne(tk.data['openid'])
        msgpq.task_done()



if __name__ == '__main__':
#飞书通知
    flask_thread = threading.Thread(target=server.setupFeishu)
    flask_thread.start()
    msg_thread = threading.Thread(target=FeishuPushThread)
    msg_thread.start()

#爬虫
    Thread=[]
    for tk in Tokens:
        t = threading.Thread(target=SpiderThread,args=(tk,))
        Thread.append(t)
        t.start()

#调度器
    producertask = threading.Thread(target=NewPostProducer)
    Thread.append(producertask)
    producertask.start()

#定时任务
    thread = threading.Thread(target=timingTask.schedule_daily_task, args=(22, 32))
    thread.start()

    flask_thread.join()
    msg_thread.join()
    producertask.join()
    for t in Thread:
        t.join()

    logger.critical("退出主线程")
