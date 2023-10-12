import redis

redis_setting = {
        "host": "redis",
        "port": 6379,
        "password": "123456",
        "db": 1,
        "max_connections": 100
    }

with redis.Redis(**redis_setting) as r:
    # keys = r.keys('*')

    r.set('test', '{"a":1,"b":2,"c":5}')

    print(r.get('test').decode())


