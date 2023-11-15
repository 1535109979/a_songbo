import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors import pool

from a_songbo.vn.util.dingding import Dingding


class EngineSchedular:
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.python_path = '/opt/anaconda3/envs/vn_new/bin/python'

    def start(self):
        self.scheduler.add_job(self.run_engine, 'cron', hour=8, minute=55, second=0)

    def run_engine(self):
        Dingding.send_msg('执行定时任务')

        subprocess.Popen([self.python_path, '/Users/edy/byt_pub/a_songbo/vn/ms/ms_engine.py'])
