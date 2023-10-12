import multiprocessing
import multiprocessing as mp


def worker(d, lock):
    with lock:
            d['a'] += 1


if __name__ == '__main__':
    lock = mp.Lock()
    shared_list = mp.Array('i', [0, 0, 0])

    d = multiprocessing.Manager().dict({'a':1})

    processes = [mp.Process(target=worker, args=(d,lock,)) for _ in range(3)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    print(shared_list[:])
    print(d)

