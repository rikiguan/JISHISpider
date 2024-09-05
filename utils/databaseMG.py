import string
import random
import time
from utils.logger import logger, printlog, genTextColor
# from elasticsearch import Elasticsearch
from pymongo import MongoClient

# 配置 Elasticsearch 和 MongoDB 的连接
mongo_client = MongoClient("mongodb://root:root@192.168.19.128:27017/")

mongo_db = mongo_client["schoolNJU"]
mongo_collection_user = mongo_db["user"]
mongo_collection_thread = mongo_db["thread"]

def getThreadCount():
    total_documents = mongo_collection_thread.count_documents({})
    return total_documents
def getUserCount():
    total_documents = mongo_collection_user.count_documents({})
    return total_documents
# 生成不重复的六位字母和数字组合的 user_id
def generate_unique_user_id():
    while True:
        user_id = ''.join(random.sample(string.ascii_letters + string.digits, 6))
        # 检查 user_id 是否已存在
        if not mongo_collection_user.find_one({"_id": user_id}):
            return user_id


# 插入文档到 MongoDB
def get_user(title, content):
    # 先检查是否存在相同的 title 和 content
    existing_doc = mongo_collection_user.find_one({"nickname": title, "headimgurl": content})
    if existing_doc:
        logger.info(f"添加用户已存在: {existing_doc['_id']}")
        return existing_doc['_id']
    else:
        user_id = generate_unique_user_id()
        document = {
            "_id": user_id,
            "nickname": title,
            "headimgurl": content
        }
        mongo_collection_user.insert_one(document)
        logger.info(f"添加新用户: {document['_id']}")
        return user_id


def getUser(user_id):
    # 查找记录是否存在
    record = mongo_collection_user.find_one({"_id": user_id})
    if record:
        # 如果记录存在，返回对应的username
        return record
    else:
        return None


def getThread(thread_id):
    # 查找记录是否存在
    record = mongo_collection_thread.find_one({"_id": thread_id})
    if record:
        # 如果记录存在，返回对应的username
        return record
    else:
        return None


def searchUserThreadFromId(userid):
    # 查询 title 和 content 中包含 key 的记录
    query = {
        "$or": [
            {"userid": {"$regex": userid, "$options": "i"}},
            {"comment_list": {
                "$elemMatch": {
                    "userid": {"$regex": userid, "$options": "i"}
                }}}
        ]
    }
    # 执行查询
    results = mongo_collection_thread.find(query)
    return results


def searchUserName(name):
    # 查询 title 和 content 中包含 key 的记录
    query = {
        "$or": [
            {"nickname": {"$regex": name, "$options": "i"}},
            {"past": {
                "$elemMatch": {
                    "nickname": {"$regex": name, "$options": "i"}
                }}}
        ]
    }
    # 执行查询
    results = mongo_collection_user.find(query)
    return results


def updateCupdatetime(postid, time):
    result = mongo_collection_thread.update_one(
        {"_id": postid},  # 查找条件
        {"$set": {"cupdatetime": time}}  # 更新操作
    )


def searchThread(key):
    # 查询 title 和 content 中包含 key 的记录
    query = {
        "$or": [
            {"title": {"$regex": key, "$options": "i"}},
            {"content": {"$regex": key, "$options": "i"}},
            {"comment": {
                "$elemMatch": {
                    "content": {"$regex": key, "$options": "i"}
                }}}
        ]
    }
    # 执行查询
    results = mongo_collection_thread.find(query)
    return results


def addToDatabaseFromListMG(list):
    for doc in list:
        addToDatabaseMG(doc)


def updateUserFromID(user_id, new_username, new_imgurl):
    existing_doc = mongo_collection_user.find_one({"nickname": new_username, "headimgurl": new_imgurl})
    # 匹配到同一用户
    if existing_doc and (not existing_doc.get("_id") == user_id) and (not new_username == "***"):

        matching_docs = mongo_collection_thread.find({
            "$or": [
                {"userid": user_id},
                {"comments.userid": user_id}
            ]
        })

        # 遍历每个符合条件的文档进行更新
        for doc in matching_docs:
            # 更新主文档中的 userid
            if doc["userid"] == user_id:
                mongo_collection_thread.update_one(
                    {"userid": user_id},
                    {"$set": {"userid": existing_doc["_id"]}}
                )

            # 更新 comments 数组中 userid
            mongo_collection_thread.update_many(
                {"_id": doc["_id"], "comments.userid": user_id},
                {"$set": {"comments.$[elem].userid": existing_doc["_id"]}},
                array_filters=[{"elem.userid": user_id}]
            )
        mongo_collection_user.delete_one({"_id": user_id})
        logger.info(f"更新用户.from{user_id}to{existing_doc["_id"]}")
        return existing_doc["_id"]
    else:
        # 查找当前文档
        current_document = mongo_collection_user.find_one({"_id": user_id})

        if current_document:
            current_username = current_document.get("nickname")
            current_imgurl = current_document.get("headimgurl")

            # 如果新数据与当前数据不一致，更新 username 和 imgurl
            if new_username != current_username or new_imgurl != current_imgurl:
                mongo_collection_user.update_one(
                    {"_id": user_id},
                    {
                        "$set": {
                            "nickname": new_username,
                            "headimgurl": new_imgurl
                        },
                        "$push": {
                            "past": {
                                "nickname": current_username,
                                "headimgurl": current_imgurl
                            }
                        }
                    }
                )
                logger.info(f"{user_id}更新用户名和头像")
            else:
                logger.info(f"{user_id}用户无变化")
        else:
            logger.error(f"{user_id}No matching document found.")
        return user_id



def addToDatabaseMG(doc):
    source = doc
    document = {
        "title": source.get("title"),
        "content": source.get("content"),
        "userid": get_user(source.get("nickname"), source.get("headimgurl")),
        "cupdatetime": 0,
        "c_count": int(source.get("c_count")),
        "view_count": int(source.get("view_count")),
        "comment_list": [],
        "sign": source.get("sign"),
        "cate_name": source.get("cate_name"),
        "state": 0,
        "p_time": int(source.get("p_time")),
        "img_paths": source.get("img_paths")
    }

    # 处理 comment_list
    if "comment_list" in source:
        comments = source["comment_list"]
        processed_comments = []

        for comment in comments:
            processed_comment = {
                "comment_id": comment.get("comment_id"),
                "userid": get_user(comment.get("nickname"), comment.get("headimgurl")),
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
                        "userid": get_user(reply.get("nickname"), reply.get("headimgurl")),
                        "content": reply.get("content")
                    }
                    processed_replies.append(processed_reply)

                processed_comment["reply_list"] = processed_replies

            processed_comments.append(processed_comment)

        document["comment_list"] = processed_comments

    # 插入到 MongoDB
    mongo_collection_thread.update_one(
        {"_id": source.get("thread_id")},  # 使用 threadid 作为唯一标识符
        {"$set": document},
        upsert=True  # 如果文档不存在，则插入
    )
    logger.info(f"插入新帖子: {source.get('thread_id')}")


def getLastPostFromMG():
    max_score_document = mongo_collection_thread.find().sort("p_time", -1).limit(1)
    max_score_document_list = list(max_score_document)
    if max_score_document_list:
        max_document = max_score_document_list[0]
        return max_document
    else:
        return None


def getLastUpdateCommentFromMG():
    one_month_ago=int(time.time())-2000000
    max_score_document = mongo_collection_thread.find(
        {"p_time": {"$gte": one_month_ago}}
    ).sort("cupdatetime", 1).limit(1)
    # max_score_document = mongo_collection_thread.find().sort("cupdatetime", 1).limit(1)
    max_score_document_list = list(max_score_document)
    if max_score_document_list:
        max_document = max_score_document_list[0]
        return max_document
    else:
        return None


def updatePost(postid, postdoc, commentsdoc):
    data = getThread(postid)
    commentsArray= dict()
    for comment in data["comment_list"]:
        commentsArray[comment.get("comment_id")] = comment
        if "reply_list" in comment:
            for re in comment["reply_list"]:
                commentsArray[re.get("comment_id")] = re


    source = postdoc
    document = {
        "title": source.get("title"),
        "content": source.get("content"),
        "userid": updateUserFromID(data.get("userid"),source.get("nickname"), source.get("headimgurl")),
        "cupdatetime": 0,
        "c_count": int(source.get("view_count")),
        "like_num": int(source.get("like_num")),
        "dislike_num": int(source.get("dislike_num")),
        "view_count": int(source.get("view_count")),
        "comment_list": [],
        "sign": source.get("sign"),
        "cate_name": source.get("cate_name"),
        "state": 0,
        "img_paths": source.get("img_paths")
    }

    # 处理 comment_list

    comments = commentsdoc
    processed_comments = []

    for comment in comments:
        Ocomment = commentsArray.get(comment.get("comment_id"))
        if Ocomment:
            userid = updateUserFromID(Ocomment.get("userid"),comment.get("nickname"),comment.get("headimgurl"))
        else:
            userid = get_user(comment.get("nickname"), comment.get("headimgurl"))

        processed_comment = {
            "comment_id": comment.get("comment_id"),
            "userid": userid,
            "content": comment.get("content"),
            "like_num": int(comment.get("like_num")),
            "dislike_num": int(comment.get("dislike_num")),
            "reply_list": []
        }
        # 处理 reply_list
        if "reply_list" in comment:

            replies = comment["reply_list"]
            processed_replies = []

            for reply in replies:

                Ore = commentsArray.get(reply.get("comment_id"))
                if Ore:
                    userid = updateUserFromID(Ore.get("userid"), reply.get("nickname"), reply.get("headimgurl"))
                else:
                    userid = get_user(reply.get("nickname"), reply.get("headimgurl"))

                processed_reply = {
                    "comment_id": reply.get("comment_id"),
                    "userid": userid,
                    "content": reply.get("content"),
                    "like_num": int(reply.get("like_num")),
                    "dislike_num": int(reply.get("dislike_num"))
                }
                processed_replies.append(processed_reply)

            processed_comment["reply_list"] = processed_replies

        processed_comments.append(processed_comment)

    document["comment_list"] = processed_comments

    # 插入到 MongoDB
    mongo_collection_thread.update_one(
        {"_id": source.get("thread_id")},  # 使用 threadid 作为唯一标识符
        {"$set": document},
        upsert=True  # 如果文档不存在，则插入
    )
    logger.info(f"更新帖子: {source.get('thread_id')}")
