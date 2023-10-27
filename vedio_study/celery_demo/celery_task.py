import time
from datetime import timedelta

import celery

# 启动命令   celery -A celery_task worker -l info
# -c 设置并发数量

backend = 'redis://:123456@localhost:6379/1'
# backend = 'rpc://admin:123456@0.0.0.0:5672/'
broker = 'pyamqp://admin:123456@0.0.0.0:5672/'


# celery -A celery_task beat   启动定时任务，另外启动一个终端执行
cel = celery.Celery('test',
                    backend=backend,
                    broker=broker)

cel.conf.timezone = 'Asia/Shanghai'
cel.conf.enable_utc = False

# 添加定时任务
cel.conf.beat_schedule = {
    'task_name': {
        'task': 'celery_task.send_msg',
        'schedule': timedelta(seconds=6),
        'args': ('yuan',)
    }
}


@cel.task
def send_email(name):
    print(f'{name} send_email  start   ')
    time.sleep(5)
    print(f'{name} send_email   end    ')

    return 'ok'


@cel.task
def send_msg(name):
    print(f'{name}  send_msg start   ')
    time.sleep(5)
    print(f'{name}  send_msg  end    ')

    return 'ok'



