import time
from datetime import datetime, timedelta
from analyze.Summary import dailyReportToAll
from utils.logger import logger


def daily_task():
    logger.info(f"执行每日任务，当前时间：{datetime.now()}")
    dailyReportToAll()



#-----------------------timing-------------------------
def get_seconds_until_target_time(target_hour, target_minute):
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)  # 如果当前时间已经过了目标时间，则设置为明天
    return (target_time - now).total_seconds()

def schedule_daily_task(target_hour, target_minute):
    while True:
        # 计算到下一个目标时间的秒数
        seconds_until_next_run = get_seconds_until_target_time(target_hour, target_minute)
        logger.info(f"等待 {seconds_until_next_run} 秒到达下一个执行时间...")
        time.sleep(seconds_until_next_run)  # 等待到达目标时间
        daily_task()  # 执行任务
