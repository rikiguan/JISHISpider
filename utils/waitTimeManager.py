from datetime import datetime
import random

SpiderClose = [1,2,3,4,5,6]
SpiderWaitMin = [30,60,60,60,60,60,60,20,20,30,30,20,20,20,30,30,30,20,20,20,20,20,30,30]

def isSpiderOpen():
    now = datetime.now()
    return not now.hour in SpiderClose

def getWaitTimeMin():
    now = datetime.now()
    return random.uniform(SpiderWaitMin[now.hour]*0.8,SpiderWaitMin[now.hour]*1.2)