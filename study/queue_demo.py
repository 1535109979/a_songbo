import queue
import threading
import time
import random
from blog_spider import craw, parse, urls


def do_craw(url_queue:queue.Queue, html_queue: queue.Queue):
    while True:
        url = url_queue.get()
        html = craw(url)
        html_queue.put(html)
        print(threading.current_thread().name, f'craw {url}', 'url_queue.size = ', url_queue.qsize())
        time.sleep(random.randint(1, 2))


def do_parse(html_queue:queue.Queue, fout):
    while True:
        html = html_queue.get()
        results = parse(html)
        for result in results:
            fout.write(str(result) + '\n')
        print(threading.current_thread().name, f'results.size=',len(results), 'html_queue.size=', html_queue.qsize())


if __name__ == '__main__':

    url_queue = queue.Queue()
    html_queue = queue.Queue()

    for url in urls:
        url_queue.put(url)

    for idx in range(3):
        t = threading.Thread(target=do_craw, args=(url_queue, html_queue,), name=f'craw{idx}')
        t.start()

    fout = open('data.txt', 'w')
    for idx in range(2):
        t = threading.Thread(target=do_parse, args=(html_queue, fout), name=f'parse{idx}')
        t.start()





