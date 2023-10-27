from concurrent.futures import ThreadPoolExecutor
from blog_spider import craw, parse, urls
from cal_time import time_consume
import time
import concurrent

def func(a, b, c):
    # 处理a、b、c三个参数的代码
    print(a)
    print(b)
    print(c)

def Push_():
    # 传入多个参数
    pool = ThreadPoolExecutor(max_workers=20)
    pool.map(lambda args: func(*args), [(1, 2, 3), (4, 5, 6)])


@time_consume
def ThreadPoolSpider():
    print('开始线程池爬取')
    pool = ThreadPoolExecutor(max_workers=20)
    htmls = pool.map(craw, urls)
    htmls = list(zip(urls, htmls))

    futures = {}
    for url, html in htmls:
        print(url, len(html))
        future = pool.submit(parse,html)
        futures[future] = url

    # for future, url in futures.items():
    #     print(url, future.result())

    for future in concurrent.futures.as_completed(futures):
        url = futures[future]
        print(url, future.result())

if __name__ == '__main__':
    ThreadPoolSpider()
    # Push_()
