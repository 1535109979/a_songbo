import asyncio

async def compute(x, y):
    print("计算 {} + {}".format(x, y))
    await asyncio.sleep(1.0)
    return x + y

async def sum():
    result1 = await compute(1, 2)
    result2 = await compute(3, 4)
    return result1 + result2

async def main():
    print("开始计算协程任务...")
    # result = await sum()
    # print("计算结果：", result)
    result1 = await compute(1, 2)
    result2 = await compute(3, 4)
    print(result1,result2)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())




