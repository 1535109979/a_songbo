import threading

# 创建一个ThreadLocal对象
thread_local = threading.local()


# 线程函数
def thread_func():
    # 每个线程都可以访问和修改自己的计数器
    if not hasattr(thread_local, 'counter'):
        thread_local.counter = 0
    for _ in range(5):
        thread_local.counter += 1
        print(threading.current_thread().name, "Counter:", thread_local.counter)


# 创建两个线程
thread1 = threading.Thread(target=thread_func)
thread2 = threading.Thread(target=thread_func)

# 启动线程
thread1.start()
thread2.start()

# 等待线程结束
thread1.join()
thread2.join()
