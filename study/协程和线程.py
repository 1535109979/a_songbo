import asyncio
import time,sys
import threading


async def func1():
    for i in range(7):
        print(f'resuming func {i}')
        await asyncio.sleep(1)


def callbackfunc(task):
    print(f'*** {str(task)} ***')


def start_thread_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func1())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    t = threading.Thread(target=start_thread_loop, args=(loop,), daemon=True)
    t.start()

    # asyncio.run_coroutine_threadsafe(func1(), loop)

    for i in range(3):
        callbackfunc(i)
        time.sleep(1)

    t.join()   # 阻塞

    print('主线程结束')


