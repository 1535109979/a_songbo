# app.py
from flask import Flask, request, jsonify
import requests
import jwt
import base64
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from Crypto.Cipher import AES
import json

from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)
app.config['WX_APPID'] = 'wx3770a6d1c0054374'
app.config['WX_SECRET'] = '1621b7c38eaa00bf4dc2de8497b434d7'

# 登录接口
@app.route('/login', methods=['POST'])
def wx_login():
    code = request.json.get('code')
    if not code:
        return jsonify({'status': 'fail', 'msg': '缺少code参数'})

    # 向微信服务器请求session_key和openid
    wx_url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": app.config['WX_APPID'],
        "secret": app.config['WX_SECRET'],
        "js_code": code,
        "grant_type": "authorization_code"
    }

    try:
        response = requests.get(wx_url, params=params)
        result = response.json()
        if 'errcode' in result:
            return jsonify({'status': 'fail', 'msg': result.get('errmsg', '微信接口错误')})

        # 生成自定义token（示例简单实现，生产环境需要更安全的方式）
        token = str(uuid.uuid4())
        print('token', token, 'openid', result['openid'])
        # 这里应该存储openid和token的关联关系（数据库或缓存）
        return jsonify({
            'status': 'success',
            'token': token,
            'openid': result['openid']
        })

    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})


# 保存用户信息接口
@app.route('/save_user', methods=['POST'])
def save_user():
    token = request.headers.get('Authorization')
    user_info = request.json.get('userInfo')

    print(token, user_info)

    # 保存用户信息到数据库（需要实现数据库操作）
    print(f"保存用户信息: {user_info}")
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # 生产环境需要正式SSL证书