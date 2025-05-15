import redis

redis_setting = {
        "host": "192.168.15.30",
        "password": "8URXPL2x3HZMi7xoGTdk3Upj",
        "db": 12,
        "port": 6379,
        "max_connections": 100
    }

with redis.Redis(**redis_setting) as r:
    keys = r.keys('*')

    for key in keys:
        print(key, r.get(key))

    # r.set('test', '{"a":1,"b":2,"c":7}', xx=True)

    # for key in keys:
    #     print(key, r.get(key))

    # r.delete(key)


    # print(r.get('test').decode())


