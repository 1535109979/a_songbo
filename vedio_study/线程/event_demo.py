import threading
import time

"""
重置代码中的event对象，使得所有的该 event对象处于待命状态
event.clear()

阻塞线程，等待event命令
event.wait()

发送event指令，使得所有设置的该event对象执行
event.set()
"""


class MyThread(threading.Thread):
    def __init__(self, event):
        super().__init__()
        self.event = event

    def run(self) -> None:
        print(f'{self.name} 线程初始化完成')
        self.event.wait()
        print(f'{self.name} 开始执行')


if __name__ == '__main__':
    event = threading.Event()

    threads = []
    [threads.append(MyThread(event)) for i in range(10)]

    event.clear()
    [t.start() for t in threads]
    time.sleep(5)

    event.set()
    [t.join() for t in threads]

