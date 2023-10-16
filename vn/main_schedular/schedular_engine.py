import multiprocessing
import os
import subprocess
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors import pool

from a_songbo.vn.util.dingding import Dingding


class EngineSchedular:
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.python_path = '/opt/anaconda3/envs/vn_new/bin/python'
        self.ms_process = None
        self.ts_process = None
        self.ss_process = None

    def start(self):
        self.scheduler.add_job(self.run_engine, 'cron', hour=8, minute=55, second=0)
        # self.scheduler.add_job(self.run_engine, 'cron', hour=13, minute=25, second=0)
        self.scheduler.add_job(self.run_engine, 'cron', hour=20, minute=55, second=0)

        # self.scheduler.add_job(self.stop_engine, 'cron', hour=11, minute=31, second=0)
        self.scheduler.add_job(self.stop_engine, 'cron', hour=15, minute=1, second=0)
        self.scheduler.add_job(self.stop_engine, 'cron', hour=0, minute=1, second=0)

        # self.scheduler.add_job(self.run_engine, 'cron', hour=17, minute=59, second=10)
        # self.scheduler.add_job(self.stop_engine, 'cron', hour=13, minute=18, second=25)
        # self.scheduler.add_job(self.stop_engine, 'interval', seconds=10)

        self.run_engine()

        self.scheduler.start()

    def run_engine(self):
        Dingding.send_msg('开始启动所有服务')

        self.ms_process = subprocess.Popen([self.python_path, '/Users/edy/byt_pub/a_songbo/vn/ms/ms_engine.py'])

        self.ts_process = subprocess.Popen([self.python_path, '/Users/edy/byt_pub/a_songbo/vn/ts/td_engine.py'])

        time.sleep(30)
        self.ss_process = subprocess.Popen([self.python_path, '/Users/edy/byt_pub/a_songbo/vn/ss/ss_engine.py'])

    def stop_engine(self):
        Dingding.send_msg('关闭所有服务')
        try:
            self.ms_process.kill()
            self.ts_process.kill()
            self.ss_process.kill()
        except:
            pass


if __name__ == '__main__':
    EngineSchedular().start()
