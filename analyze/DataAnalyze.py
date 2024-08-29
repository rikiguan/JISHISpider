from utils.logger import logger
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import rcParams
from utils.databaseES import es

rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体作为中文字体
index_name = "school_new"


def getAllDocNum():
    response = es.count(index=index_name)
    total_count = response['count']
    logger.info(f"查询数据库索引 '{index_name}' 中的总数据量: {total_count}")
    return total_count


def getDayDocNum():
    now = datetime.now()
    start_of_yesterday = now - timedelta(days=1)
    end_of_yesterday = now
    # 构造查询，使用 count API 获取每小时的数据量
    query = {
        "query": {
            "range": {
                "p_time": {
                    "gte": int(start_of_yesterday.timestamp()),  # 大于或等于该小时的开始时间
                    "lt": int(end_of_yesterday.timestamp())  # 小于该小时的结束时间
                }
            }
        }
    }

    # 调用 count API 获取记录数
    response = es.count(index=index_name, body=query)  # 修改为你的索引名称
    total_count = response['count']
    logger.info(f"查询数据库今日索引 '{index_name}' 中的总数据量: {total_count}")
    return total_count


def genTimeCountImg():
    now = datetime.now()
    start_of_yesterday = now - timedelta(days=1)
    end_of_yesterday = now

    hourly_count = {}
    for hour in range(24):
        # 计算每个小时的开始时间和结束时间
        start_hour = start_of_yesterday + timedelta(hours=hour)
        end_hour = start_hour + timedelta(hours=1)
        # 构造查询，使用 count API 获取每小时的数据量
        query = {
            "query": {
                "range": {
                    "p_time": {
                        "gte": int(start_hour.timestamp()),  # 大于或等于该小时的开始时间
                        "lt": int(end_hour.timestamp())  # 小于该小时的结束时间
                    }
                }
            }
        }
        # 调用 count API 获取记录数
        response = es.count(index=index_name, body=query)  # 修改为你的索引名称
        hourly_count[hour] = response['count']

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
