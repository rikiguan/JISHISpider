import json
import threading
from utils import waitTimeManager
from utils.TaskManager import task_manager
import JiShiRequest
import utils.waitTimeManager
from conf import *
from tasks.feishuPushTask import FeishuPushThread
from utils.useLog import log_thread
import time
from feishu import server
from tasks import timingTask
from utils.QueueModule import msgpq,pq
from utils.TaskManager import Task, TaskManager
from utils.databaseES import es, getLastPostFromES, addToDatabaseFromList
from utils.logger import logger

import tasks #important



@log_thread()
def taskHandler(tag,rq,tk):
    handler = task_manager.get_handler_with_task(tk)
    return handler(rq, tk, tag)


def SpiderThread(token):
    failNum = 0
    tag = token[0][:5]
    rq = JiShiRequest.JiShi(token)
    while failNum < 10:
        tk = pq.get()
        logger.info(f'任务获取{tk}')
        if not taskHandler(tag,rq,tk):
            failNum += 1
            logger.error(f'任务执行失败,任务为{tk}')
            tk.priority=1
            pq.put(tk)
        pq.task_done()
    logger.error(f'爬虫线程{tag}退出{failNum}')
    msgpq.put(Task(1, 'error', {'tag': tag,'msg': failNum}))
def NewPostProducer():
    while True:
        res = getLastPostFromES()
        if res:
            pq.put(Task(2, "newPost", {'from_id': res['_id'], 'from_time': res['_source']['p_time']}))
        while not waitTimeManager.isSpiderOpen():
            time.sleep(60)
        time.sleep(waitTimeManager.getWaitTimeMin()*60)


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
