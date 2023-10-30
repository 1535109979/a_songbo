from byt_persistent.cache.rabbit_queue_client import get_rabbit_queue_client
from byt_config.utils import config_loader

config_loader.load_config()

rabbit_client = get_rabbit_queue_client()
rabbit_client.publish(channel='4C.task_schedule_config.python3', message='test data')


