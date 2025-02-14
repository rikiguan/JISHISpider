from analyze.DataAnalyze import genTimeCountImg, getAllDocNum, getDayDocNum, getAllUser
from analyze.informTemplate import daySummaryTemplate
from utils.useLog import thread_count, request_count
from conf import *


def dailyReportToAll():
    for open_id in informid:
        daySummaryTemplate(open_id, getAllDocNum(), getDayDocNum(), genTimeCountImg(), thread_count, request_count,getAllUser())


def dailyReportToOne(open_id):
    daySummaryTemplate(open_id, getAllDocNum(), getDayDocNum(), genTimeCountImg(), thread_count, request_count,getAllUser())


if __name__ == '__main__':
    daySummaryTemplate(getAllDocNum(), getDayDocNum(), genTimeCountImg(), thread_count, request_count,getAllUser())
