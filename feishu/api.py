#! /usr/bin/env python3.8
import json
import os
import logging
import requests
from requests_toolbelt import MultipartEncoder
from conf import *
from utils.logger import logger


# const
TENANT_ACCESS_TOKEN_URI = "/open-apis/auth/v3/tenant_access_token/internal"
MESSAGE_URI = "/open-apis/im/v1/messages"


class MessageApiClient(object):
    def __init__(self, app_id, app_secret, lark_host):
        self._app_id = app_id
        self._app_secret = app_secret
        self._lark_host = lark_host
        self._tenant_access_token = ""

    @property
    def tenant_access_token(self):
        return self._tenant_access_token

    def send_text_with_open_id(self, open_id, content):
        self.send("open_id", open_id, "text", content)

    def send_img_with_open_id(self, open_id, path):
        content = {
            "image_key": self.upload_image(path)
        }
        self.send("open_id", open_id, "image", json.dumps(content))

    def send_file_with_open_id(self, open_id, path):
        content = {
            "file_key": self.upload_file(path)
        }
        self.send("open_id", open_id, "file", json.dumps(content))

    def send_interactiveTemplate_with_open_id(self, open_id, template_id,data):
        content = {"type": "template", "data": {"template_id": template_id, "template_version_name": "1.0.0",
                                                "template_variable": data}}
        self.send("open_id", open_id, "interactive", json.dumps(content))

    def send_divider_with_open_id(self, open_id, text):
        content = {
            "type": "divider",
            "params": {
                "divider_text": {
                    "text": text,
                }
            }

        }
        self.send("open_id", open_id, "system", json.dumps(content))

    def upload_file(self, file_path):
        url = "https://open.feishu.cn/open-apis/im/v1/files"
        form = {'file_type': 'stream',
                'file_name': os.path.basename(file_path),
                'file': (os.path.basename(file_path), open(file_path, 'rb'),
                         'text/plain')}  # 需要替换具体的path  具体的格式参考  https://www.w3school.com.cn/media/media_mimeref.asp
        multi_form = MultipartEncoder(form)
        headers = {
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        headers['Content-Type'] = multi_form.content_type
        resp = requests.request("POST", url, headers=headers, data=multi_form)
        content = resp.json()
        if content.get("code") == 0:
            return content['data']['file_key']
        else:
            return Exception("Call Api Error, errorCode is %s" % content["code"])

    def upload_image(self, image_path):
        with open(image_path, 'rb') as f:
            image = f.read()
            resp = requests.post(
            url='https://open.feishu.cn/open-apis/image/v4/put/',
            headers={
                "Authorization": "Bearer " + self.tenant_access_token,
            },
            files={
                "image": image
            },
            data={
                "image_type": "message"
            },
            stream=True)
        content = resp.json()
        if content.get("code") == 0:
            return content['data']['image_key']
        else:

            return Exception("Call Api Error, errorCode is %s" % content["code"])


    def send(self, receive_id_type, receive_id, msg_type, content):
        # send message to user, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        self._authorize_tenant_access_token()
        url = "{}{}?receive_id_type={}".format(
            self._lark_host, MESSAGE_URI, receive_id_type
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }

        req_body = {
            "receive_id": receive_id,
            "content": content,
            "msg_type": msg_type,
        }
        resp = requests.post(url=url, headers=headers, json=req_body)
        MessageApiClient._check_error_response(resp)

    def _authorize_tenant_access_token(self):
        # get tenant_access_token and set, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/auth-v3/auth/tenant_access_token_internal
        url = "{}{}".format(self._lark_host, TENANT_ACCESS_TOKEN_URI)
        req_body = {"app_id": self._app_id, "app_secret": self._app_secret}
        response = requests.post(url, req_body)
        MessageApiClient._check_error_response(response)
        self._tenant_access_token = response.json().get("tenant_access_token")

    @staticmethod
    def _check_error_response(resp):
        # check if the response contains error information
        if resp.status_code != 200:
            resp.raise_for_status()
        response_dict = resp.json()
        code = response_dict.get("code", -1)
        if code != 0:
            logging.error(response_dict)
            raise LarkException(code=code, msg=response_dict.get("msg"))


class LarkException(Exception):
    def __init__(self, code=0, msg=None):
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        return "{}:{}".format(self.code, self.msg)

    __repr__ = __str__
