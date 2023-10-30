import asyncio


# 阻塞式运行

# async def coro():
#     print("Start blocking task...")
#     await asyncio.sleep(2)  # 模拟进行阻塞操作
#     print("Blocking task done!")
#
# async def main():
#     await asyncio.gather(coro(), coro())
#
# if __name__ == "__main__":
#     asyncio.run(main())

# 非阻塞式运行

async def coro(num):
    print(f"Start non-blocking task {num}...")
    await asyncio.sleep(1)
    print(f"Non-blocking task {num} done!")


async def main():
    tasks = [asyncio.create_task(coro(i)) for i in range(3)]
    await asyncio.wait(tasks)

if __name__ == "__main__":

    asyncio.run(main())

