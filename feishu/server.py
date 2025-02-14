import json
import logging
import time
import uuid
import requests

from utils.TaskManager import Task
from utils.logger import logger
from feishu.api import MessageApiClient
from feishu.event import MessageReceiveEvent, UrlVerificationEvent, EventManager
from flask import Flask, jsonify, g, request
from conf import *
from utils.QueueModule import msgpq

app = Flask(__name__)

# init service
message_api_client = MessageApiClient(APP_ID, APP_SECRET, LARK_HOST)
event_manager = EventManager()

@app.before_request
def before_request():
    g.start = time.time()
    g.request_id = str(uuid.uuid4())

@app.after_request
def after_request(response):
    duration = time.time() - g.start
    logger.info(f'{request.method} {request.path} {response.status_code} {duration:.2f}s', extra={'request_id': g.request_id})
    return response

@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    sender_id = req_data.event.sender.sender_id
    message = req_data.event.message

    if message.message_type != "text":
        logger.warn("Other types of messages have not been processed yet")
        return jsonify()

    # get open_id and text_content
    open_id = sender_id.open_id
    text_content = message.content
    logger.info(f'从{open_id}收到数据{text_content}')
    text =json.loads(text_content)['text']
    if(text == '总结'):
        msgpq.put(Task(2, 'summary', {'openid': open_id}))
    if ("搜名字" in text):
        content = text.split("搜名字", 1)[1].strip()
        msgpq.put(Task(2, 'searchUserName', {'openid': open_id, 'content': content}))
    if ("搜用户" in text):
        content = text.split("搜用户", 1)[1].strip()
        msgpq.put(Task(2, 'searchUserId', {'openid': open_id, 'content': content}))
    if ("搜ID内容" in text):
        content = text.split("搜ID内容", 1)[1].strip()
        msgpq.put(Task(2, 'searchContentFromUserID', {'openid': open_id, 'content': content}))
    if ("搜内容" in text):
        content = text.split("搜内容", 1)[1].strip()
        msgpq.put(Task(2, 'searchContent', {'openid': open_id, 'content': content}))
    if ("订阅" in text):
        content=''
        msgpq.put(Task(2, 'subscript', {'openid': open_id, 'content': content}))
    if ("清除" in text):
        content=''
        msgpq.put(Task(2, 'delsubscript', {'openid': open_id, 'content': content}))

    return jsonify()


@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


@app.route("/", methods=["POST"])
def callback_event_handler():
    # init callback instance and handle
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)

    return event_handler(event)

def setupFeishu():
    app.run(host="0.0.0.0", port=3000, debug=False,threaded=True,use_reloader=False)

if __name__ == "__main__":
    # init()
    pass
