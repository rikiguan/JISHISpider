from elasticsearch import Elasticsearch

# 连接到 Elasticsearch
es = Elasticsearch(["http://192.168.1.10:9200"])  # 如果你使用的是 Docker，可以换成容器的网络名称

# 检查连接状态
if es.ping():
    print("Connected to Elasticsearch")
else:
    print("Could not connect to Elasticsearch")
