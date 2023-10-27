from apscheduler.schedulers.blocking import BlockingScheduler

# 创建一个调度器实例
scheduler = BlockingScheduler()


# 定义一个作业函数
def job():
    print('作业执行')


# # 添加一个监听器函数，在作业开始和结束时打印日志
# def listener(event):
#     if event.exception:
#         print('作业出错：%s' % event.exception)
#     elif event.code == "EVENT_JOB_EXECUTED":
#         print('作业已完成：%s' % event.job_id)
#     elif event.code == "EVENT_JOB_ERROR":
#         print('作业出错：%s' % event.job_id)


# 将监听器添加到调度器
# scheduler.add_listener(listener)

# 添加一个作业，每隔5秒钟执行一次job函数
scheduler.add_job(job)

# 启动调度器
scheduler.start()
