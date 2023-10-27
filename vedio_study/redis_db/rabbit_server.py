from datetime import datetime

from byt_config.configs.local_config import LocalConfig
from byt_persistent.cache.rabbit_queue_client import get_rabbit_queue_client
from byt_config.utils import config_loader
from byt_persistent.service.task_schedule_config_service import TaskScheduleConfigService

config_loader.load_config()
print('---LocalConfig.machine_tag:',LocalConfig.machine_tag)
rabbit_client = get_rabbit_queue_client()
cache_name = TaskScheduleConfigService.get_cache_names(
            group_name='system_restart_task',
            title='system restart service',
            machine_tag=LocalConfig.machine_tag)


def handle_message(message):
    message = eval(message.decode())[0]
    if message['group_name'] == 'system_restart_task' and message['tasks']:
        print(f'----{datetime.now()}--- restart server --- tasks:',message['tasks'])


rabbit_client.subscribe(channel_to_handle_fn={cache_name: handle_message})
rabbit_client.unblock_listen(daemon=True)


while 1:
    pass

