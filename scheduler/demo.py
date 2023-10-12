import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# 创建一个调度器实例
scheduler = BlockingScheduler()

# 定义一个作业函数
def job():
    print('作业执行时间：', datetime.datetime.now())

# 添加一个作业，每隔5秒钟执行一次job函数
# scheduler.add_job(job, 'interval', seconds=5)
#
# scheduler.add_job(job, 'date', run_date=datetime.datetime(2022, 1, 1, 0, 0, 0))

# 添加一个作业，每天的特定时间执行job函数
scheduler.add_job(job, 'cron', hour=11, minute=25, second=30)

# 启动调度器
scheduler.start()
