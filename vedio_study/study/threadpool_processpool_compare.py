import math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from cal_time import time_consume

primes = [112272535095293] * 100


def is_prime(n):
    # 判断是否时素数
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return True
    sqrt_n = int(math.floor(math.sqrt(n)))

    for i in range(3, sqrt_n+1, 2):
        if n % i == 0:
            return False

    return True


@time_consume
def single_thread():
    print('开始单线程计算')
    for number in primes:
        is_prime(number)


@time_consume
def multi_thread():
    print('开始多线程计算')
    # with ThreadPoolExecutor(max_workers=20) as pool:
    pool = ThreadPoolExecutor(max_workers=20)
    res = pool.map(is_prime, primes)
    pool.shutdown(wait=True)
    # for r in res:
    #     print(r)


@time_consume
def multi_process():
    print('开始多进程计算')
    with ProcessPoolExecutor() as pool:
        res = pool.map(is_prime, primes)
        pool.shutdown(wait=True)
        print(res)


def run():
    single_thread()
    multi_thread()
    multi_process()


if __name__ == '__main__':
    run()






