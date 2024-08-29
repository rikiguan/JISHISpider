#!/usr/bin/env python3.8
import json
import logging
import time
import uuid
import requests
from utils.logger import logger
from utils.QueueModule import  Task
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
    if(json.loads(text_content)['text'] == 'summary'):
        msgpq.put(Task(2, 'summary', {'openid': open_id}))

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
    app.run(host="0.0.0.0", port=3000, debug=True,threaded=True,use_reloader=False)

if __name__ == "__main__":
    # init()
    app.run(host="0.0.0.0", port=3000, debug=True)
