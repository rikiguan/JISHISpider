import string
import random
from elasticsearch import Elasticsearch
from pymongo import MongoClient

# 配置 Elasticsearch 和 MongoDB 的连接
es = Elasticsearch("http://localhost:9200",timeout=600 )
mongo_client = MongoClient("mongodb://mongoadmin:secret@localhost:27017/")

# 指定 Elasticsearch 的索引名称和 MongoDB 的数据库、集合名称
es_index = "school_new"
mongo_db = mongo_client["schoolNJU"]
mongo_collection = mongo_db["user"]

# 从 Elasticsearch 中查询数据
query = {
    "query": {
        "match_all": {}
    }
}

# 生成不重复的六位字母和数字组合的 user_id
def generate_unique_user_id():
    while True:
        user_id = ''.join(random.sample(string.ascii_letters + string.digits, 6))
        # 检查 user_id 是否已存在
        if not mongo_collection.find_one({"_id": user_id}):
            return user_id


# 插入文档到 MongoDB
def insert_document(title, content):
    # 先检查是否存在相同的 title 和 content
    existing_doc = mongo_collection.find_one({"nickname": title, "headimgurl": content})
    if existing_doc:
        print(f"文档已存在，跳过插入: {existing_doc['_id']}")
        return existing_doc['_id']
    else:
        user_id = generate_unique_user_id()
        document = {
            "_id": user_id,
            "nickname": title,
            "headimgurl": content
        }
        mongo_collection.insert_one(document)
        print(f"插入新文档: {document['_id']}")
        return user_id

def updateUser():
    # 使用scroll API从Elasticsearch中获取所有文档
    scroll_time = "2m"  # 设置 scroll 的时间
    es_results = es.search(index=es_index, body=query, scroll=scroll_time, size=1000)

    # 获取初始的 scroll_id 和第一批文档
    scroll_id = es_results['_scroll_id']
    hits = es_results['hits']['hits']

    # 循环获取并插入所有文档
    while len(hits) > 0:
        for hit in hits:
            # 提取 title 和 content 字段
            title = hit['_source'].get('nickname', '')
            content = hit['_source'].get('headimgurl', '')
            print('>', end='')

            # 插入文档到 MongoDB
            insert_document(title, content)

        # 使用scroll_id继续获取下一批文档
        es_results = es.scroll(scroll_id=scroll_id, scroll=scroll_time)
        scroll_id = es_results['_scroll_id']
        hits = es_results['hits']['hits']



    print("操作完成！")


# 从 Elasticsearch 中查询数据
query = {
    "query": {
        "exists": {
            "field": "comment_list"
        }
    }
}
query ={
  "query": {
    "nested": {
      "path": "comment_list",
      "query": {
        "match_all": {}
      }
    }
  }
}

def reply():
    # 使用scroll API从Elasticsearch中获取所有文档
    scroll_time = "2m"  # 设置 scroll 的时间
    es_results = es.search(index=es_index, body=query, scroll=scroll_time, size=1000)

    # 获取初始的 scroll_id 和第一批文档
    scroll_id = es_results['_scroll_id']
    hits = es_results['hits']['hits']

    # 用于存储所有的 nickname
    all_nicknames = set()
    print(hits)
    # 循环获取并处理所有文档
    while len(hits) > 0:
        for hit in hits:
            source = hit['_source']
            # 提取 comment_list
            comment_list = source.get('comment_list', [])
            for comment in comment_list:
                # 提取 comment_list 中的 nickname
                comment_nickname = comment.get('nickname')
                comment_headimgurl = comment.get('headimgurl')
                if comment_nickname:
                    insert_document(comment_nickname,comment_headimgurl)

                # 提取 reply_list
                reply_list = comment.get('reply_list', [])
                for reply in reply_list:
                    # 提取 reply_list 中的 nickname
                    reply_nickname = reply.get('nickname')
                    reply_headimgurl=reply.get('headimgurl')
                    if reply_nickname:
                        insert_document(reply_nickname,reply_headimgurl)

        # 使用scroll_id继续获取下一批文档
        es_results = es.scroll(scroll_id=scroll_id, scroll=scroll_time)
        scroll_id = es_results['_scroll_id']
        hits = es_results['hits']['hits']


# 设置 scroll 的时间
scroll_time = "10m"

# 执行初始 scroll 查询
query = {
    "query": {
        "match_all": {}
    }
}
mongo_collectionT = mongo_db["thread"]
es_results = es.search(index=es_index, body=query, scroll=scroll_time, size=500)
scroll_id = es_results['_scroll_id']

# 插入文档到 MongoDB
while True:
    # 使用 scroll_id 检索更多数据
    es_results = es.scroll(scroll_id=scroll_id, scroll=scroll_time)

    # 如果没有更多数据，退出循环
    if not es_results['hits']['hits']:
        break

    # 处理和插入数据到 MongoDB
    for hit in es_results['hits']['hits']:
        source = hit['_source']
        document = {
            "title": source.get("title"),
            "content": source.get("content"),
            "userid": insert_document(source.get("nickname"), source.get("headimgurl")),
            "cupdatetime": 0,
            "c_count":int(source.get("c_count")),
            "view_count":int(source.get("view_count")),
            "comment_list": [],
            "sign": source.get("sign"),
            "cate_name": source.get("cate_name"),
            "state":0,
            "p_time":int(source.get("p_time")),
            "img_paths":source.get("img_paths")
        }

        # 处理 comment_list
        if "comment_list" in source:
            comments = source["comment_list"]
            processed_comments = []

            for comment in comments:
                processed_comment = {
                    "comment_id": comment.get("comment_id"),
                    "userid": insert_document(comment.get("nickname"), comment.get("headimgurl")),
                    "content": comment.get("content"),
                    "reply_list": []
                }

                # 处理 reply_list
                if "reply_list" in comment:
                    replies = comment["reply_list"]
                    processed_replies = []

                    for reply in replies:
                        processed_reply = {
                            "comment_id": reply.get("comment_id"),
                            "userid":insert_document(reply.get("nickname"),reply.get("headimgurl")),
                            "content": reply.get("content")
                        }
                        processed_replies.append(processed_reply)

                    processed_comment["reply_list"] = processed_replies

                processed_comments.append(processed_comment)

            document["comment_list"] = processed_comments

        # 插入到 MongoDB
        mongo_collectionT.update_one(
            {"_id": source.get("thread_id")},  # 使用 threadid 作为唯一标识符
            {"$set": document},
            upsert=True  # 如果文档不存在，则插入
        )
        print(f"Inserted/Updated document with threadid: {source.get('thread_id')}")

    # 获取新的 scroll_id
    scroll_id = es_results['_scroll_id']

# 清理滚动上下文
es.clear_scroll(scroll_id=scroll_id)

print("操作完成！")