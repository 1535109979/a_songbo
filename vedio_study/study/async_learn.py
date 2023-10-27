import asyncio

import aiohttp
from blog_spider import urls


# async def async_craw(url):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as resp:
#             result = await resp.text()
#             print(url, len(result))
#
# loop = asyncio.get_event_loop()
# tasks = [loop.create_task(async_craw(url)) for url in urls]
# loop.run_until_complete((asyncio.wait(tasks)))

import asyncio
import aiohttp


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def download_pages(urls):
    # 创建异步会话
    async with aiohttp.ClientSession() as session:
        # 创建任务列表
        tasks = []
        for url in urls:
            # 提交任务到事件循环中
            task = asyncio.ensure_future(fetch(session, url))
            tasks.append(task)
        # 等待所有任务完成
        responses = await asyncio.gather(*tasks)
        # 将结果按照原始顺序输出
        results = [response for _, response in sorted(zip(urls, responses))]
        return results

loop = asyncio.get_event_loop()
# 执行异步下载任务
pages = loop.run_until_complete(download_pages(urls))
# 输出结果
# print(pages)
for page in pages:
    print(len(page))


