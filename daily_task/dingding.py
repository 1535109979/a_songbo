import base64
import json
from datetime import datetime

import requests

from a_songbo.vn.util.lock import instance_synchronized


class Dingding:

    url = ('https://oapi.dingtalk.com/robot/send?access_token='
           '2b336337436ea0b4edb5c4117d584b01b613c9eaf102c284e27ae5cfb92d4b8b')

    @classmethod
    @instance_synchronized
    def send_msg(cls, text: str, isatall=False):
        # print('-----', datetime.now())
        # print(text)
        # print('-----')
        # return
        data = {
            "msgtype": "markdown",
            "markdown": {
                        "title": '## ',
                        "text": datetime.now().strftime('%Y-%m-%d %H:%M:%S  \n') + text
                    },
            "at": {
                "isAtAll": isatall
            }
        }

        requests.post(cls.url, headers={'content-type': "application/json"},
                      data=json.dumps(data))

    @classmethod
    def send_image(cls, image_path, isatall=False):

        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')

        payload = {
            "msgtype": "image",
            "image": {
                "base64": image_base64
            }
        }

        response = requests.post(cls.url, json=payload)
        print(response.text)


if __name__ == '__main__':
    # Dingding.send_msg(text="第一行  \n第二行")
    Dingding.send_image('account_value.png')

