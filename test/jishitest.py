import JiShiRequest
from conf import *
from tasks.JISHITask import updateHistoryTask
from utils.TaskManager import Task
rq = JiShiRequest.JiShi(Tokens[0])
# res = rq.requestPostComment("1862795471","lWhrY5qdZmyakw==")

updateHistoryTask(rq,Task(2, "newPost", {'post_id': "1847225424"}),"haha")
#1846523969
# res = rq.requestPostInfo("1854273169")
