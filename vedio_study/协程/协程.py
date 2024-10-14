import asyncio
import time

def add2(x):
    print(x + 2)
    return x + 2


async def add3(x):
    print('---')
    return x + 3


async def funca(x):
    print('in test a')
    await asyncio.sleep(3)
    print('resuming a')
    return x


async def funcb(x):
    print('in test b')
    await asyncio.sleep(1)
    print('resuming b')
    return x


def callbackfunc(task):
    print('callback', task.result())


async def main():
    start = time.time()

    # resulta = await tesa(1)    # 串行
    # resultb = await tesb(2)
    resulta , resultb = await asyncio.gather(funca(1), funcb(2))    # 并行

    print('test a result :',resulta)
    print('test b result :',resultb)
    print('use time:',time.time() - start)


async def main2():   # 并行
    start = time.time()
    taska = asyncio.ensure_future(funca(1))
    taskb = asyncio.ensure_future(funcb(2))
    # taska = asyncio.create_task(funca(1))
    # taskb = asyncio.create_task(funcb(2))

    taska.add_done_callback(callbackfunc)

    # await taska
    # await taskb
    # await asyncio.wait([taska,taskb])
    resulta, resultb = await asyncio.gather(taska,taskb)

    print('test a result :',taska.result())
    print('test b result :',taskb.result())
    print('use time:',time.time() - start)


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())





