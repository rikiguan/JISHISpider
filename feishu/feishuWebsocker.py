import base64
import hashlib
import hmac
import json
import time

import requests


class FeiShuRobot:

    def __init__(self, robot_id, secret, app_id, app_secret):
        self.robot_id = robot_id
        self.secret = secret
        self.app_id = app_id
        self.app_secret = app_secret

    def gen_sign(self):
        # 拼接timestamp和secret
        timestamp = int(round(time.time() * 1000))
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        print(timestamp, sign)
        return str(timestamp), str(sign)

    def get_token(self):
        """获取应用token，需要用app_id和app_secret，主要是上传图片需要用到token"""
        url = r"https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {"Content-Type": "text/plain"}
        Body = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        r = requests.post(url, headers=headers, json=Body)
        print(r.text)
        return json.loads(r.text)['tenant_access_token']

    def upload_image(self, image_path):
        """上传图片"""
        with open(image_path, 'rb') as f:
            image = f.read()
        resp = requests.post(
            url='https://open.feishu.cn/open-apis/image/v4/put/',
            headers={'Authorization': "Bearer " + self.get_token()},
            files={
                "image": image
            },
            data={
                "image_type": "message"
            },
            stream=True)
        resp.raise_for_status()
        content = resp.json()
        if content.get("code") == 0:
            return content['data']['image_key']
        else:
            return Exception("Call Api Error, errorCode is %s" % content["code"])

    def send_text(self, text):
        """发送普通消息"""
        try:
            url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.robot_id}"
            headers = {"Content-Type": "text/plain"}

            timestamp, sign = self.gen_sign()
            data = {
                "timestamp": timestamp,
                "sign": sign,
                "msg_type": "text",
                "content": {
                    "text": text
                }
            }
            r = requests.post(url, headers=headers, json=data)
            print("发送飞书成功")

            return r.text
        except Exception as e:
            print("发送飞书失败:", e)

    def send_img(self, path):
        """发送图片消息"""
        url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.robot_id}"
        headers = {"Content-Type": "text/plain"}
        data = {
            "msg_type": "image",
            "content": {
                "image_key": self.upload_image(path)
            }
        }
        r = requests.post(url, headers=headers, json=data)
        return r.text

    def send_markdown(self, text):
        """发送富文本消息"""
        url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.robot_id}"
        headers = {"Content-Type": "text/plain"}
        data = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "注意咯！！注意咯！！！"
                    },
                    "template": "red"
                },
                "elements": [{"tag": "div",
                              "text": {"content": text,
                                       "tag": "lark_md"}}]}
        }
        r = requests.post(url, headers=headers, json=data)
        return r.text

    def send_card(self, Text):
        """发送卡片消息"""
        try:
            url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.robot_id}"
            headers = {"Content-Type": "text/plain"}
            data = {
                "msg_type": "interactive",
                "card": {
                    "elements": [{
                        "tag": "div",
                        "text": {
                            "content": "**西湖**，位于浙江省杭州市西湖区龙井路1号，杭州市区西部，景区总面积49平方千米，汇水面积为21.22平方千米，湖面面积为6.38平方千米。",
                            "tag": "lark_md"
                        }
                    }, {
                        "actions": [{
                            "tag": "button",
                            "text": {
                                "content": "更多景点介绍 :玫瑰:",
                                "tag": "lark_md"
                            },
                            "url": "https://www.example.com",
                            "type": "default",
                            "value": {}
                        }],
                        "tag": "action"
                    }],
                    "header": {
                        "title": {
                            "content": "今日旅游推荐",
                            "tag": "plain_text"
                        }
                    }
                }
            }
            r = requests.post(url, headers=headers, json=data)
            print(r.text)
            return r.text

        except Exception as e:
            print("发送飞书失败:", e)





if __name__ == '__main__':
    pass
