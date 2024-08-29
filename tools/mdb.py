from pymongo import MongoClient
mongo_client = MongoClient("mongodb://mongoadmin:secret@localhost:27017/")

# 指定 Elasticsearch 的索引名称和 MongoDB 的数据库、集合名称


mongo_db = mongo_client["schoolNJU"]
mongo_collection = mongo_db["thread"]


# 批量更新文档，将 posttime 字段的 string 类型转换为 int 类型
mongo_collection.update_many(
    {"_id": {"$type": "string"}},
    [{"$set": {"_id": {"$toInt": "$p_time"}}}]
)
# invalid_docs = mongo_collection.find({"p_time": {"$not": {"$regex": "^\d+$"}}})
#
# for doc in invalid_docs:
#     print(doc)  # 打印这些文档以便手动检查