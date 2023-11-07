import asyncio
import time,sys
import threading
import concurrent
from concurrent import futures
import functools
import subprocess
import os


def ping(url):
    print('PING 线程:',threading.current_thread(),'进程id：',os.getpid())
    time.sleep(4)
    print(url)
    return url


async def func1():
    print('func 1')
    await asyncio.sleep(1)
    print('func 1:',threading.current_thread())
    print('resuming func 1')
    return 'func 1'


async def func2():
    print('func 2')
    await asyncio.sleep(1)
    print('func 2:',threading.current_thread())
    print('resuming func 2')
    return 'func 2'


def start_thread_loop(loop):
    print('子线程 loop 线程 id : ',threading.current_thread())
    asyncio.set_event_loop(loop)
    loop.run_forever()


def callbackfunc(task):
    print('task finish result : ',task.result())


async def main():
    t1 = time.time()
    # 使用 loop.create_task 创建 task 对象，返回 asyncio.task.Task 对象
    task1 = loop.create_task(func1())
    task2 = loop.create_task(func2())

    task3 = asyncio.run_coroutine_threadsafe(func1(),loop)
    task4 = asyncio.run_coroutine_threadsafe(func2(),loop)

    task5 = asyncio.ensure_future(func1())
    task6 = asyncio.ensure_future(func2())

    result = asyncio.gather(task1,task2,task3,task4,task5,task6)
    print(result)
    print('use timer:',time.time() - t1)


async def main2():
    result = asyncio.gather(func1(),func2())
    print(result)


if __name__ == '__main__':
    print('main thread')
    loop = asyncio.get_event_loop()
    task7 = loop.run_in_executor(None, ping, 'www.baidu.com')
    task8 = loop.run_in_executor(None, ping, 'www.qq.com')
    print(task7,task8)

    t = threading.Thread(target=start_thread_loop, args=(loop,))
    t.start()

    asyncio.run_coroutine_threadsafe(main(),loop)

    print('main finish')

