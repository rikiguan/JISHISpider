from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体作为中文字体
# 初始化Elasticsearch客户端
es = Elasticsearch("http://localhost:9200")  # 请根据实际情况配置


# 获取昨天的开始时间和结束时间
now = datetime.now()
start_of_yesterday =datetime.now()-timedelta(days=1)
end_of_yesterday = datetime.now()
print(start_of_yesterday)

# 循环获取每个小时的数据量
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
                    "lt": int(end_hour.timestamp())      # 小于该小时的结束时间
                }
            }
        }
    }

    # 调用 count API 获取记录数
    response = es.count(index="school_new", body=query)  # 修改为你的索引名称
    hourly_count[hour] = response['count']

hours = list(range(24))
extra_info = list(range(start_of_yesterday.hour,24))+list(range(0,end_of_yesterday.hour))
counts = [hourly_count.get(hour, 0) for hour in hours]
print(hours)
print(counts)
# 绘制折线图
plt.figure(figsize=(10, 6))
plt.xticks(hours, [f'{info}h' for hour, info in zip(hours, extra_info)])
plt.plot(hours, counts, marker='|', linestyle='-', color='b')
plt.xlabel('小时')
plt.ylabel('记录数')
plt.title('昨天每小时记录数')
plt.xticks(hours)  # 确保每个小时都显示在X轴
plt.grid(True)

# 保存折线图为图片
plt.savefig('weeklySummary.png')

# 显示折线图
plt.show()