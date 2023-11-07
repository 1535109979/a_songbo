import multiprocessing
import os
import time
import random
from threadpool_processpool_compare import is_prime
from cal_time import time_consume


data = [random.randint(1000, 10000) for i in range(10000)]


chunk_size = len(data) // multiprocessing.cpu_count()
chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]


def cal_prime(num_list, que):
    res = []
    for num in num_list:
        res.append(is_prime(num))
    # print(len(res))
    que.put(list(zip(num_list, res)))


@time_consume
def run():
    que = multiprocessing.Queue()
    processes = []
    for chunk in chunks:
        p = multiprocessing.Process(target=cal_prime, args=(chunk,que))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print('All workers finished')

    while not que.empty():
        result = que.get()
        # print(result)
        print(len(result))


if __name__ == '__main__':
    run()


