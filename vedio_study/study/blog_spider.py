import requests
import threading
from cal_time import time_consume
import queue
from bs4 import BeautifulSoup


urls = [f'https://www.cnblogs.com/#p{page}' for page in range(1,51)]


def craw(url):
    r = requests.get(url)
    return r.text


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', class_='post-item-title')
    return [(link['href'], link.get_text()) for link in links]


@time_consume
def single_thread():
    print('开始执行单线程')
    for url in urls:
        craw(url)


@time_consume
def multi_thread():
    print('开始执行多线程')
    threads = []
    for url in urls:
        threads.append(threading.Thread(target=craw,args=(url,)))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()




if __name__ == '__main__':
    url = urls[2]
    print(url)
    html = craw(url)
    print(html)
    res = parse(html)
    print(res)
    # print(parse(craw(urls[2])))
    quit()

    # single_thread()
    # multi_thread()


    for result in parse(craw(urls[2])):
        print(result)

