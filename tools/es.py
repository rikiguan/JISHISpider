from elasticsearch import Elasticsearch

# 创建 Elasticsearch 客户端
# es = Elasticsearch("http://localhost:9200")
# es = Elasticsearch("http://my-es:9200")
es = Elasticsearch(["http://192.168.1.10:9200"])
my_index="school_new"
# 查询最近的十条数据
response = es.search(
    index=my_index,
    body={
        "size": 2,
        "sort": [{"p_time": {"order": "desc"}}],
        "_source": ["_id"]
    }
)

# 获取文档的 _id 列表
ids = [hit["_id"] for hit in response["hits"]["hits"]]
print(ids)
# 构建 bulk 删除请求
actions = [{"delete": {"_index": my_index, "_id": doc_id}} for doc_id in ids]

# 批量删除
es.bulk(body=actions)
