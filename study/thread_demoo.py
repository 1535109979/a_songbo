import threading
import time


def consume_queue():
    for i in range(5):
        print(i)
        time.sleep(1)


if __name__ == '__main__':
    num_threads = 5
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=consume_queue)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()