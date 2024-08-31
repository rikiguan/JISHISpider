import json
import time

import random

from utils.TaskManager import TaskManager, Task
from utils.databaseES import addToDatabaseFromList
from utils.TaskManager import task_manager
from utils.QueueModule import msgpq,pq

def responseVerifyANDJSON(res):
    if res.status_code != 200:
        return None
    data = json.loads(res.text)
    if data['errno'] != 0:
        return None
    return data

@task_manager.register('newPost')
def getNewPostNumTask(rq, tk, tag):
    response = rq.requestGetNewPostNum(tk.data['from_id'], tk.data['from_time'])

    data = responseVerifyANDJSON(response)
    if not data:
        return False
    num = int(data['data']['count'])
    if(num == 0):
        return True
    time.sleep(random.uniform(5, 10))

    response1 = rq.requestGetNewPost(tk.data['from_id'], tk.data['from_time'])
    data = responseVerifyANDJSON(response1)
    if not data:
        return False

    list = data['data']['list']
    addToDatabaseFromList(tag, list)
    returnnum = len(list)
    if (num == returnnum):
        return True
    time.sleep(random.uniform(5, 10))

    timestamp = list[-1]['p_time']
    while returnnum < 2 * num and int(timestamp) > int(tk.data['from_time']):
        response2 = rq.requestMainPageFromTime(timestamp)
        if response2.status_code != 200:
            return False
        data2 = json.loads(response2.text)
        if data2['errno'] != 0 or len(data2['data']['list']) == 0:
            return False
        list2 = data2['data']['list']
        addToDatabaseFromList(tag, list2)
        timestamp = list2[-1]['p_time']
        returnnum += len(list2)
        time.sleep(random.uniform(5,10))
    return True