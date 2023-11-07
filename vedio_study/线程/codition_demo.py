import threading
import random
import time

# 定义一个共享的队列
queue = []
# 定义一个Condition对象
condition = threading.Condition()


# 生产者线程函数
def producer():
    while True:
        # 获取锁
        condition.acquire()
        # 如果队列已满，则等待
        while len(queue) >= 5:
            condition.wait()
        # 生成随机数并放入队列
        num = random.randint(1, 100)
        queue.append(num)
        print("Produced:", num)
        # 通知消费者线程可以消费了
        condition.notify()
        # 释放锁
        condition.release()
        time.sleep(1)


# 消费者线程函数
def consumer():
    while True:
        # 获取锁
        condition.acquire()
        # 如果队列为空，则等待
        while len(queue) == 0:
            condition.wait()
        # 从队列中取出随机数并处理
        num = queue.pop(0)
        print("Consumed:", num)
        # 通知生产者线程可以生产了
        condition.notify()
        # 释放锁
        condition.release()
        time.sleep(1)

# 创建生产者线程和消费者线程
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

# 启动线程
producer_thread.start()
consumer_thread.start()

# 等待线程结束
producer_thread.join()
consumer_thread.join()
