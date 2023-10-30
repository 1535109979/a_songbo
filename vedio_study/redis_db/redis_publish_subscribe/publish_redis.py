import redis

redis_setting = {
        "host":"localhost",
        "port":6379,
        "password":"123456",
        "db": 1,
        "max_connections":100
    }


# 创建Redis客户端连接
r = redis.Redis(**redis_setting)

r.publish('test', 'Value changed')




