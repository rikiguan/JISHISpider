from elasticsearch import Elasticsearch, NotFoundError
from utils.logger import logger, printlog, genTextColor

index_name = "school_new"
es = Elasticsearch("http://192.168.1.10:9200")

def addToDatabaseFromList(tag,list):
    for doc in list:
        document_id = doc['thread_id']
        try:
            response = es.get(index=index_name, id=document_id)
            update_response = es.update(index=index_name, id=document_id, body={"doc": doc})
            logger.info(f"文档已存在{document_id}{response}{update_response}")
            printlog(tag,genTextColor('r','×')+f'文档已存在{document_id}')
        except NotFoundError:
            insert_response = es.index(index=index_name, id=document_id, body=doc)
            logger.info(f"文档不存在{document_id}{insert_response}")
            printlog(tag, genTextColor('g', '√') + f'文档不存在{document_id}')

def getLastPostFromES():
    response = es.search(
        index=index_name,
        body={
            "size": 1,
            "sort": [{"p_time": {"order": "desc"}}]
        }
    )
    logger.info(f"最新记录{response['hits']['hits'][0]['_id']}时间戳{response['hits']['hits'][0]['_source']['p_time']}")
    return response['hits']['hits'][0]

