import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# 模拟数据库数据
users = [
    {"id": 1, "name": "Alice", "age": 25},
    {"id": 2, "name": "Bob", "age": 30},
    {"id": 3, "name": "Charlie", "age": 35}
]

use_password = {
    'admin': 'password123'
}

# 获取所有用户
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print(data)
    username = data.get('username')
    password = data.get('password')
    if username in use_password and use_password[username] == password:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/saveUserInfo', methods=['POST'])
def save_user_info():
    data = request.json
    user_info = data.get('userInfo')
    openid = data.get('openid')
    # 保存用户信息到数据库
    # 这里只是一个示例，实际应用中需要将用户信息保存到数据库中
    print(f"Received user info: {user_info}")
    return jsonify({'message': '用户信息已保存'})

@app.route('/api/submit', methods=['POST'])
def submit_data():
    data = request.json
    stock_name = data.get('stockName')
    initial_amount = data.get('initialAmount')
    replenish_fall = data.get('replenishFall')

    # 在这里可以将数据保存到数据库或其他存储中
    print(f"收到数据：股票名称={stock_name}, 开仓金额={initial_amount}, 补仓跌幅={replenish_fall}")

    return jsonify({"message": "数据提交成功"})

if __name__ == '__main__':
    app.run(debug=True)