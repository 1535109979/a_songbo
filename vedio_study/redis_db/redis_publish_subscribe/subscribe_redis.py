import redis
redis_setting = {
        "host":" 0.0.0.0",
        "port": 6379,
        "password": "123456",
        "db": 1,
        "max_connections": 100
    }
# 创建Redis客户端连接
r = redis.Redis(**redis_setting)


# 定义消息处理函数
def handle_message(message):
    # 处理接收到的更新消息
    print("Received update:", message)


# 订阅频道并关联消息处理函数
p = r.pubsub()
p.subscribe('test')

# 循环监听消息
for message in p.listen():
    # 调用消息处理函数处理接收到的消息
    handle_message(message)
