from utils.databaseMG import getThreadCount, mongo_collection_thread
from utils.logger import logger
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import rcParams
# from utils.databaseES import es
import matplotlib.font_manager as fm

# 字体文件路径
font_path = 'fonts/SourceHanSansCN-Normal.ttf'

# 添加字体到字体管理器
prop = fm.FontProperties(fname=font_path)

# 设置 Matplotlib 使用自定义字体
rcParams['font.family'] = prop.get_name()



def getAllDocNum():
    total_count = getThreadCount()
    logger.info(f"查询数据库索引 thread中的总数据量: {total_count}")
    return total_count


def getDayDocNum():
    now = datetime.now()
    start_of_yesterday = now - timedelta(days=1)
    end_of_yesterday = now
    today_records_count = mongo_collection_thread.count_documents({
        "p_time": {"$gte": int(start_of_yesterday.timestamp()), "$lt": int(end_of_yesterday.timestamp())}
    })
    logger.info(f"查询数据库今日索引 thread 中的总数据量: {today_records_count}")
    return today_records_count


def genTimeCountImg():
    now = datetime.now()
    start_of_yesterday = now - timedelta(days=1)
    end_of_yesterday = now

    hourly_count = {}
    for hour in range(24):
        # 计算每个小时的开始时间和结束时间
        start_hour = start_of_yesterday + timedelta(hours=hour)
        end_hour = start_hour + timedelta(hours=1)
        today_records_count = mongo_collection_thread.count_documents({
            "p_time": {"$gte": int(start_hour.timestamp()), "$lt": int(end_hour.timestamp())}
        })
        hourly_count[hour] = today_records_count

    hours = list(range(24))
    extra_info = list(range(start_of_yesterday.hour, 24)) + list(range(0, end_of_yesterday.hour))
    counts = [hourly_count.get(hour, 0) for hour in hours]

    plt.figure(figsize=(10, 6))
    plt.xticks(hours, [f'{info}h' for hour, info in zip(hours, extra_info)])
    plt.plot(hours, counts, marker='|', linestyle='-', color='b')
    plt.xlabel('小时')
    plt.ylabel('记录数')
    plt.title('过去24h记录数')
    plt.grid(False)
    plt.savefig('data/weeklySummary.png')
    return 'data/weeklySummary.png'
