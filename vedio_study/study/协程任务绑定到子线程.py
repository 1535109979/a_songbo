import asyncio
import time,sys
import threading
import concurrent
from concurrent import futures
import functools
import subprocess
import os


def ping(url):
    print('线程:',threading.current_thread(),'进程id：',os.getpid())
    time.sleep(2)
    # os.system(f'ping {url}')
    print(url)
    print('block finsh')


async def func1():
    # print('func 1')
    for i in range(5):
        await asyncio.sleep(1)
        # print('func 1:',threading.current_thread())
        print(f'in func1 {i}')
    return 'func 1'


async def func2():
    print('func 2')
    await asyncio.sleep(1)
    print('func 2:',threading.current_thread())
    print('in func 2')
    return 'func 2'


def callbackfunc(task):
    print('*** {task} ***',task)


async def main():
    task1 = loop.create_task(func1())
    task1.add_done_callback(callbackfunc)

    task2 = loop.create_task(func2())
    task2.add_done_callback(callbackfunc)

    result = await asyncio.gather(task1,task2)
    print(result)


def start_thread_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())

    # t1 = threading.Thread(target=ping,args=('www.baidu.com',))
    # t2 = threading.Thread(target=ping,args=('www.yangyanxing.com',))
    # t3 = threading.Thread(target=ping,args=('www.qq.com',))
    # t1.start()
    # t2.start()
    # t3.start()

    t = threading.Thread(target=start_thread_loop,args=(loop,),daemon=True).start()

    # threadingexecutor = concurrent.futures.ThreadPoolExecutor(20)
    # processexecutor = concurrent.futures.ProcessPoolExecutor(20)
    #
    # # 选择使用 多线程 还是 多进程 执行
    # loop.run_in_executor(processexecutor,ping,'www.baidu.com')
    # loop.run_in_executor(processexecutor,ping,'www.yangyanxing.com')
    # loop.run_in_executor(processexecutor,ping,'www.qq.com')

    asyncio.run_coroutine_threadsafe(func1(),loop)
    asyncio.run_coroutine_threadsafe(func2(),loop)

    for i in range(30):
        # callbackfunc(i)
        time.sleep(1)

    print('主线程结束')

