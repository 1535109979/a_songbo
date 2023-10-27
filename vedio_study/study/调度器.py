import datetime
import time
import sched


def time_printer():
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('do func time :', ts)
    loop_monitor()


def loop_monitor():
    s = sched.scheduler(time.time, time.sleep)  # 生成调度器
    s.enter(5, 1, time_printer, ())
    s.run()


if __name__ == "__main__":
    loop_monitor()
